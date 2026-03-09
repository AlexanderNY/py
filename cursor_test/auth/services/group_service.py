"""Сервис для работы с рабочими группами."""

from typing import Dict, List, Optional

from database import get_db_connection


async def get_user_group_membership(user_id: int) -> Optional[Dict]:
    """Возвращает группу пользователя и его роль в ней, если есть."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT g.id, g.name, g.created_at, g.created_by_user_id, gm.role_in_group, gm.joined_at
                FROM group_members gm
                JOIN groups g ON g.id = gm.group_id
                WHERE gm.user_id = %s
                """,
                (user_id,),
            )
            row = await cur.fetchone()
    if not row:
        return None
    return {
        "group_id": row[0],
        "group_name": row[1],
        "created_at": row[2],
        "created_by_user_id": row[3],
        "role_in_group": row[4],
        "joined_at": row[5],
    }


async def get_group_member_user_ids(group_id: int) -> List[int]:
    """Возвращает список user_id всех участников группы (для статистики в core)."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT user_id FROM group_members WHERE group_id = %s",
                (group_id,),
            )
            rows = await cur.fetchall()
    return [r[0] for r in rows]


async def get_group_by_id(group_id: int, include_members: bool = False) -> Optional[Dict]:
    """Возвращает группу по id. Если include_members=True, подтягивает участников с username, email, tariff."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, name, created_at, created_by_user_id
                FROM groups WHERE id = %s
                """,
                (group_id,),
            )
            row = await cur.fetchone()
    if not row:
        return None
    group = {
        "id": row[0],
        "name": row[1],
        "created_at": row[2],
        "created_by_user_id": row[3],
        "members": None,
    }
    if include_members:
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT gm.user_id, u.username, u.email, u.tariff, u.role, gm.role_in_group, gm.joined_at
                    FROM group_members gm
                    JOIN users u ON u.id = gm.user_id
                    WHERE gm.group_id = %s
                    ORDER BY gm.role_in_group, gm.joined_at
                    """,
                    (group_id,),
                )
                members_rows = await cur.fetchall()
        group["members"] = [
            {
                "user_id": r[0],
                "username": r[1],
                "email": r[2],
                "tariff": r[3] or "free",
                "role": r[4],
                "role_in_group": r[5],
                "joined_at": r[6],
            }
            for r in members_rows
        ]
    return group


async def get_my_group(user_id: int, current_user_role: str) -> Optional[Dict]:
    """
    Возвращает группу текущего пользователя.
    Для manager — с полным списком участников; для author — без списка других авторов.
    """
    membership = await get_user_group_membership(user_id)
    if not membership:
        return None
    group_id = membership["group_id"]
    include_members = membership["role_in_group"] == "manager" or current_user_role == "admin"
    group = await get_group_by_id(group_id, include_members=include_members)
    if not group:
        return None
    group["role_in_group"] = membership["role_in_group"]
    return group


async def create_group(user_id: int, name: str, current_user_role: str) -> Dict:
    """
    Создаёт группу. Только пользователь с ролью manager, не состоящий ни в какой группе.
    Добавляет создателя в group_members с role_in_group='manager'.
    """
    if current_user_role not in ("manager", "admin"):
        raise PermissionError("Only manager or admin can create a group")
    existing = await get_user_group_membership(user_id)
    if existing:
        raise ValueError("User is already in a group")

    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO groups (name, created_by_user_id)
                VALUES (%s, %s)
                RETURNING id, name, created_at, created_by_user_id
                """,
                (name, user_id),
            )
            row = await cur.fetchone()
            if not row:
                raise RuntimeError("Failed to create group")
            group_id = row[0]
            await cur.execute(
                """
                INSERT INTO group_members (group_id, user_id, role_in_group)
                VALUES (%s, %s, 'manager')
                """,
                (group_id, user_id),
            )
    return {
        "id": row[0],
        "name": row[1],
        "created_at": row[2],
        "created_by_user_id": row[3],
        "role_in_group": "manager",
        "members": [],
    }


async def update_group(
    group_id: int, name: str, requested_by_user_id: int, requested_by_role: str
) -> Dict:
    """Обновляет название группы. Только менеджер этой группы или admin."""
    membership = await get_user_group_membership(requested_by_user_id)
    if requested_by_role != "admin":
        if not membership or membership["group_id"] != group_id:
            raise PermissionError("Not a member of this group")
        if membership["role_in_group"] != "manager":
            raise PermissionError("Only group manager can update the group")

    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE groups SET name = %s WHERE id = %s RETURNING id, name, created_at, created_by_user_id",
                (name, group_id),
            )
            row = await cur.fetchone()
    if not row:
        raise ValueError("Group not found")
    return {
        "id": row[0],
        "name": row[1],
        "created_at": row[2],
        "created_by_user_id": row[3],
    }


async def add_member_by_email(
    group_id: int, email: str, requested_by_user_id: int, requested_by_role: str
) -> Dict:
    """
    Добавляет в группу пользователя по email с ролью author.
    Только менеджер этой группы или admin. Пользователь не должен быть в другой группе.
    """
    membership = await get_user_group_membership(requested_by_user_id)
    if requested_by_role != "admin":
        if not membership or membership["group_id"] != group_id:
            raise PermissionError("Not a member of this group")
        if membership["role_in_group"] != "manager":
            raise PermissionError("Only group manager can add members")

    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, username, email, tariff FROM users WHERE email = %s", (email,))
            user_row = await cur.fetchone()
            if not user_row:
                raise ValueError("User with this email not found")
            target_user_id = user_row[0]
            await cur.execute(
                "SELECT 1 FROM group_members WHERE user_id = %s",
                (target_user_id,),
            )
            if await cur.fetchone():
                raise ValueError("User is already in a group")
            await cur.execute(
                """
                INSERT INTO group_members (group_id, user_id, role_in_group)
                VALUES (%s, %s, 'author')
                """,
                (group_id, target_user_id),
            )
            await cur.execute(
                "SELECT joined_at FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, target_user_id),
            )
            joined_row = await cur.fetchone()
    return {
        "user_id": target_user_id,
        "username": user_row[1],
        "email": user_row[2],
        "tariff": user_row[3] or "free",
        "role_in_group": "author",
        "joined_at": joined_row[0] if joined_row else None,
    }


async def remove_member(
    group_id: int, member_user_id: int, requested_by_user_id: int, requested_by_role: str
) -> None:
    """Удаляет участника из группы. Менеджер группы или admin. Нельзя удалить единственного менеджера."""
    membership = await get_user_group_membership(requested_by_user_id)
    if requested_by_role != "admin":
        if not membership or membership["group_id"] != group_id:
            raise PermissionError("Not a member of this group")
        if membership["role_in_group"] != "manager":
            raise PermissionError("Only group manager can remove members")

    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT role_in_group FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, member_user_id),
            )
            row = await cur.fetchone()
            if not row:
                raise ValueError("User is not a member of this group")
            if row[0] == "manager":
                raise ValueError("Cannot remove the group manager")
            await cur.execute(
                "DELETE FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, member_user_id),
            )


async def get_all_groups_with_members() -> List[Dict]:
    """Список всех групп с участниками (для admin)."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, name, created_at, created_by_user_id FROM groups ORDER BY name
                """
            )
            groups_rows = await cur.fetchall()
    result = []
    for row in groups_rows:
        g = {
            "id": row[0],
            "name": row[1],
            "created_at": row[2],
            "created_by_user_id": row[3],
            "members": [],
        }
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT gm.user_id, u.username, u.email, u.tariff, u.role, gm.role_in_group, gm.joined_at
                    FROM group_members gm
                    JOIN users u ON u.id = gm.user_id
                    WHERE gm.group_id = %s
                    ORDER BY gm.role_in_group, gm.joined_at
                    """,
                    (row[0],),
                )
                members_rows = await cur.fetchall()
        g["members"] = [
            {
                "user_id": r[0],
                "username": r[1],
                "email": r[2],
                "tariff": r[3] or "free",
                "role": r[4],
                "role_in_group": r[5],
                "joined_at": r[6],
            }
            for r in members_rows
        ]
        result.append(g)
    return result
