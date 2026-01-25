from typing import Dict, Optional
from database import get_db_connection
from services.password_service import hash_password, verify_password
from services.token_service import (
    save_refresh_token,
    save_email_verification_token,
    get_email_verification_token,
    delete_email_verification_token,
    save_password_reset_token,
    get_password_reset_token,
    delete_password_reset_token
)
from utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
    create_email_verification_token,
    create_password_reset_token
)
from utils.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    EmailAlreadyVerifiedError,
    TokenNotFoundError
)


async def register_user(username: str, email: str, password: str) -> Dict:
    """Регистрация нового пользователя."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # Проверка существования пользователя
            await cur.execute(
                "SELECT id FROM users WHERE username = %s OR email = %s",
                (username, email)
            )
            existing_user = await cur.fetchone()
            
            if existing_user:
                raise UserAlreadyExistsError("User with this username or email already exists")
            
            # Хеширование пароля
            password_hash = hash_password(password)
            
            # Создание пользователя (роль по умолчанию 'guest')
            await cur.execute(
                """
                INSERT INTO users (username, email, password_hash, role)
                VALUES (%s, %s, %s, 'guest')
                RETURNING id, username, email, role, is_email_verified, created_at
                """,
                (username, email, password_hash)
            )
            user_row = await cur.fetchone()
            
            if not user_row:
                raise RuntimeError("Failed to create user")
            
            user_id = user_row[0]
            user_role = user_row[3]
            
            # Создание токенов
            access_token = create_access_token(user_id, user_role)
            refresh_token = create_refresh_token(user_id, user_role)
            
            # Сохранение refresh токена
            await save_refresh_token(user_id, refresh_token)
            
            # Создание токена для верификации email
            email_verification_token = create_email_verification_token(user_id)
            await save_email_verification_token(user_id, email_verification_token)
            
            return {
                "user_id": user_id,
                "username": user_row[1],
                "email": user_row[2],
                "role": user_role,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "email_verification_token": email_verification_token
            }


async def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Аутентификация пользователя по логину и паролю."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, username, email, password_hash, role, is_email_verified
                FROM users WHERE username = %s
                """,
                (username,)
            )
            user_row = await cur.fetchone()
            
            if not user_row:
                return None
            
            user_id, db_username, db_email, password_hash, user_role, is_email_verified = user_row
            
            # Проверка пароля
            if not verify_password(password, password_hash):
                return None
            
            # Создание токенов
            access_token = create_access_token(user_id, user_role)
            refresh_token = create_refresh_token(user_id, user_role)
            
            # Сохранение refresh токена
            await save_refresh_token(user_id, refresh_token)
            
            return {
                "user_id": user_id,
                "username": db_username,
                "email": db_email,
                "role": user_role,
                "is_email_verified": is_email_verified,
                "access_token": access_token,
                "refresh_token": refresh_token
            }


async def verify_email_token(token: str) -> bool:
    """Верификация email по токену."""
    user_id = await get_email_verification_token(token)
    
    if not user_id:
        raise TokenNotFoundError("Invalid or expired email verification token")
    
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # Проверка, не верифицирован ли уже email
            await cur.execute(
                "SELECT is_email_verified FROM users WHERE id = %s",
                (user_id,)
            )
            user_row = await cur.fetchone()
            
            if not user_row:
                raise UserNotFoundError("User not found")
            
            if user_row[0]:
                raise EmailAlreadyVerifiedError("Email is already verified")
            
            # Обновление статуса верификации
            await cur.execute(
                "UPDATE users SET is_email_verified = TRUE WHERE id = %s",
                (user_id,)
            )
            
            # Удаление токена
            await delete_email_verification_token(token)
            
            return True


async def reset_password(token: str, new_password: str) -> bool:
    """Сброс пароля по токену."""
    user_id = await get_password_reset_token(token)
    
    if not user_id:
        raise TokenNotFoundError("Invalid or expired password reset token")
    
    # Хеширование нового пароля
    password_hash = hash_password(new_password)
    
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # Обновление пароля
            await cur.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (password_hash, user_id)
            )
            
            # Удаление токена
            await delete_password_reset_token(token)
            
            # Отзыв всех refresh токенов пользователя (безопасность)
            from auth.services.token_service import revoke_all_refresh_tokens
            await revoke_all_refresh_tokens(user_id)
            
            return True


async def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Получение пользователя по ID."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, username, email, role, is_email_verified, created_at
                FROM users WHERE id = %s
                """,
                (user_id,)
            )
            user_row = await cur.fetchone()
            
            if not user_row:
                return None
            
            return {
                "id": user_row[0],
                "username": user_row[1],
                "email": user_row[2],
                "role": user_row[3],
                "is_email_verified": user_row[4],
                "created_at": user_row[5]
            }


async def update_user_profile(user_id: int, username: Optional[str] = None, email: Optional[str] = None) -> Dict:
    """Обновление профиля пользователя."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # Проверка существования пользователя
            await cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not await cur.fetchone():
                raise UserNotFoundError("User not found")
            
            # Проверка уникальности username и email
            if username:
                await cur.execute(
                    "SELECT id FROM users WHERE username = %s AND id != %s",
                    (username, user_id)
                )
                if await cur.fetchone():
                    raise UserAlreadyExistsError("Username already taken")
            
            if email:
                await cur.execute(
                    "SELECT id FROM users WHERE email = %s AND id != %s",
                    (email, user_id)
                )
                if await cur.fetchone():
                    raise UserAlreadyExistsError("Email already taken")
            
            # Обновление полей
            updates = []
            params = []
            
            if username:
                updates.append("username = %s")
                params.append(username)
            
            if email:
                updates.append("email = %s")
                updates.append("is_email_verified = FALSE")
                params.append(email)
            
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(user_id)
                
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s RETURNING id, username, email, role, is_email_verified, created_at"
                await cur.execute(query, params)
                user_row = await cur.fetchone()
                
                if user_row:
                    return {
                        "id": user_row[0],
                        "username": user_row[1],
                        "email": user_row[2],
                        "role": user_row[3],
                        "is_email_verified": user_row[4],
                        "created_at": user_row[5]
                    }
            
            # Если ничего не обновлялось, возвращаем текущего пользователя
            return await get_user_by_id(user_id)


async def initiate_password_reset(email: str) -> str:
    """Инициация сброса пароля (создание токена)."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            user_row = await cur.fetchone()
            
            if not user_row:
                # Не раскрываем информацию о существовании пользователя
                # Все равно создаем токен, но он будет невалидным
                return ""
            
            user_id = user_row[0]
            
            # Создание токена сброса пароля
            reset_token = create_password_reset_token(user_id)
            await save_password_reset_token(user_id, reset_token)
            
            return reset_token


async def get_all_users() -> list[Dict]:
    """Получение списка всех пользователей (только для администраторов)."""
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, username, email, role, is_email_verified, created_at
                FROM users
                ORDER BY created_at DESC
                """
            )
            rows = await cur.fetchall()
            
            return [
                {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "role": row[3],
                    "is_email_verified": row[4],
                    "created_at": row[5]
                }
                for row in rows
            ]

