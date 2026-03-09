"""Роутер для рабочих групп."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List

from schemas import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupMemberResponse,
    AddMemberRequest,
)
from services import group_service
from dependencies import get_current_user, get_admin_user


router = APIRouter(prefix="/groups", tags=["groups"])


def _group_to_response(g: Dict, with_members: bool = True) -> GroupResponse:
    members = None
    if with_members and g.get("members") is not None:
        members = [
            GroupMemberResponse(
                user_id=m["user_id"],
                username=m["username"],
                email=m["email"],
                tariff=m["tariff"],
                role_in_group=m["role_in_group"],
                joined_at=m["joined_at"],
            )
            for m in g["members"]
        ]
    return GroupResponse(
        id=g["id"],
        name=g["name"],
        created_at=g["created_at"],
        created_by_user_id=g.get("created_by_user_id"),
        role_in_group=g.get("role_in_group"),
        members=members,
    )


@router.get("/my", response_model=GroupResponse)
async def get_my_group(current_user: Dict = Depends(get_current_user)) -> GroupResponse:
    """Получение своей группы. Для менеджера — с списком участников; для автора — только название и роль."""
    group = await group_service.get_my_group(
        current_user["id"],
        current_user.get("role", "user"),
    )
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not in any group",
        )
    return _group_to_response(group, with_members=bool(group.get("members")))


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    body: GroupCreate,
    current_user: Dict = Depends(get_current_user),
) -> GroupResponse:
    """Создание группы. Доступно только пользователю с ролью manager, не состоящему в группе."""
    try:
        group = await group_service.create_group(
            current_user["id"],
            body.name,
            current_user.get("role", "user"),
        )
        return _group_to_response(group, with_members=True)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    body: GroupUpdate,
    current_user: Dict = Depends(get_current_user),
) -> GroupResponse:
    """Обновление названия группы. Только менеджер этой группы."""
    try:
        await group_service.update_group(
            group_id,
            body.name,
            current_user["id"],
            current_user.get("role", "user"),
        )
        full_group = await group_service.get_group_by_id(group_id, include_members=True)
        if full_group:
            membership = await group_service.get_user_group_membership(current_user["id"])
            full_group["role_in_group"] = membership.get("role_in_group") if membership else None
        return _group_to_response(full_group, with_members=True)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{group_id}/members", status_code=status.HTTP_201_CREATED)
async def add_member(
    group_id: int,
    body: AddMemberRequest,
    current_user: Dict = Depends(get_current_user),
):
    """Добавление участника в группу по email. Только менеджер группы."""
    try:
        member = await group_service.add_member_by_email(
            group_id,
            body.email,
            current_user["id"],
            current_user.get("role", "user"),
        )
        return member
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    group_id: int,
    user_id: int,
    current_user: Dict = Depends(get_current_user),
) -> None:
    """Удаление участника из группы. Только менеджер группы. Нельзя удалить менеджера группы."""
    try:
        await group_service.remove_member(
            group_id,
            user_id,
            current_user["id"],
            current_user.get("role", "user"),
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/my-member-ids")
async def get_my_group_member_ids(current_user: Dict = Depends(get_current_user)) -> List[int]:
    """
    Возвращает список user_id участников группы текущего пользователя.
    Только для менеджера группы или admin. Иначе 404.
    """
    membership = await group_service.get_user_group_membership(current_user["id"])
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not in any group",
        )
    if membership["role_in_group"] != "manager" and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group manager can get member ids",
        )
    return await group_service.get_group_member_user_ids(membership["group_id"])


@router.get("/group-members-user-ids/{group_id}")
async def get_group_member_user_ids_for_statistics(
    group_id: int,
    current_user: Dict = Depends(get_current_user),
) -> List[int]:
    """
    Возвращает список user_id участников группы.
    Только если текущий пользователь — менеджер этой группы или admin.
    """
    membership = await group_service.get_user_group_membership(current_user["id"])
    if current_user.get("role") != "admin":
        if not membership or membership["group_id"] != group_id or membership["role_in_group"] != "manager":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only group manager or admin can get member ids",
            )
    ids = await group_service.get_group_member_user_ids(group_id)
    return ids


@router.get("", response_model=List[GroupResponse])
async def get_all_groups(admin_user: Dict = Depends(get_admin_user)) -> List[GroupResponse]:
    """Список всех групп с участниками. Только admin."""
    groups = await group_service.get_all_groups_with_members()
    return [_group_to_response(g, with_members=True) for g in groups]
