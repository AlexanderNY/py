"""Обработчик авторизации Telegram."""

import logging
from typing import Dict, Optional
from telethon import TelegramClient
from telethon.errors import (
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PhoneNumberInvalidError,
    FloodWaitError
)
from database import get_db_connection, release_db_connection
from .notification_service import notification_service


logger = logging.getLogger(__name__)


class AuthHandler:
    """Обработчик авторизации Telegram клиентов."""
    
    async def submit_phone_code(
        self,
        user_id: int,
        code: str,
        client: TelegramClient
    ) -> Dict:
        """Обрабатывает код подтверждения от пользователя.
        
        Args:
            user_id: ID пользователя
            code: Код подтверждения
            client: TelegramClient для авторизации
            
        Returns:
            Словарь с результатом авторизации
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                # Получаем профиль и phone_code_hash
                await cur.execute(
                    """
                    SELECT auth_phone_number, auth_phone_code_hash
                    FROM tg_profiles
                    WHERE user_id = %s
                    """,
                    (user_id,)
                )
                row = await cur.fetchone()
                
                if not row:
                    return {
                        "success": False,
                        "error": "Profile not found"
                    }
                
                phone_number, phone_code_hash = row
                
                if not phone_code_hash:
                    return {
                        "success": False,
                        "error": "Phone code hash not found. Please request code again."
                    }
                
                try:
                    # Пытаемся авторизоваться с кодом
                    await client.sign_in(
                        phone_number,
                        code,
                        phone_code_hash=phone_code_hash
                    )
                    
                    # Успешная авторизация
                    await cur.execute(
                        """
                        UPDATE tg_profiles
                        SET auth_state = 'authorized',
                            auth_phone_code_hash = NULL,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                        """,
                        (user_id,)
                    )
                    
                    logger.info(f"User {user_id} successfully authorized")
                    return {
                        "success": True,
                        "message": "Authorization successful"
                    }
                
                except SessionPasswordNeededError:
                    # Требуется 2FA пароль
                    await cur.execute(
                        """
                        UPDATE tg_profiles
                        SET auth_state = 'pending_password',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                        """,
                        (user_id,)
                    )
                    
                    await notification_service.send_2fa_notification(user_id)
                    
                    logger.info(f"User {user_id} needs 2FA password")
                    return {
                        "success": False,
                        "requires_password": True,
                        "message": "2FA password required"
                    }
                
                except PhoneCodeInvalidError:
                    await notification_service.send_error_notification(
                        user_id,
                        "Неверный код подтверждения. Попробуйте еще раз."
                    )
                    return {
                        "success": False,
                        "error": "Invalid code"
                    }
                
                except PhoneCodeExpiredError:
                    await notification_service.send_error_notification(
                        user_id,
                        "Код подтверждения истек. Запросите новый код."
                    )
                    await cur.execute(
                        """
                        UPDATE tg_profiles
                        SET auth_state = 'pending_code',
                            auth_phone_code_hash = NULL,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                        """,
                        (user_id,)
                    )
                    return {
                        "success": False,
                        "error": "Code expired"
                    }
        
        except Exception as e:
            logger.error(f"Error submitting phone code for user {user_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            await release_db_connection(conn)
    
    async def submit_2fa_password(
        self,
        user_id: int,
        password: str,
        client: TelegramClient
    ) -> Dict:
        """Обрабатывает 2FA пароль от пользователя.
        
        Args:
            user_id: ID пользователя
            password: Пароль двухфакторной аутентификации
            client: TelegramClient для авторизации
            
        Returns:
            Словарь с результатом авторизации
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                try:
                    # Авторизация с паролем
                    await client.sign_in(password=password)
                    
                    # Успешная авторизация
                    await cur.execute(
                        """
                        UPDATE tg_profiles
                        SET auth_state = 'authorized',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                        """,
                        (user_id,)
                    )
                    
                    logger.info(f"User {user_id} successfully authorized with 2FA")
                    return {
                        "success": True,
                        "message": "Authorization successful"
                    }
                
                except Exception as e:
                    await notification_service.send_error_notification(
                        user_id,
                        f"Ошибка авторизации: {str(e)}"
                    )
                    return {
                        "success": False,
                        "error": str(e)
                    }
        
        except Exception as e:
            logger.error(f"Error submitting 2FA password for user {user_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            await release_db_connection(conn)


auth_handler = AuthHandler()
