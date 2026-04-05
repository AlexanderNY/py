"""Сохранение сессии instagrapi и статуса авторизации в БД."""

import json
import logging
from typing import Any, Dict, Optional

from database import get_db_connection, release_db_connection

logger = logging.getLogger(__name__)


def _json_for_pg(settings_dict: Dict[str, Any]) -> str:
    return json.dumps(settings_dict, default=str)


async def persist_instagram_session(user_id: int, settings_dict: Dict[str, Any]) -> None:
    """Сохраняет instagrapi get_settings() в instagram_profiles.instagrapi_session."""
    if not settings_dict:
        return
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE instagram_profiles
                SET instagrapi_session = %s::jsonb,
                    instagram_last_auth_error = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                """,
                (_json_for_pg(settings_dict), user_id),
            )
    except Exception as e:
        logger.error("persist_instagram_session user_id=%s: %s", user_id, e, exc_info=True)
    finally:
        await release_db_connection(conn)


async def set_instagram_verification_code(user_id: int, code: str) -> None:
    """Устанавливает одноразовый код 2FA до следующего успешного входа бота."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE instagram_profiles
                SET instagram_verification_code = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                """,
                (code.strip(), user_id),
            )
    except Exception as e:
        logger.warning("set_instagram_verification_code user_id=%s: %s", user_id, e)
    finally:
        await release_db_connection(conn)


async def clear_instagram_verification_code(user_id: int) -> None:
    """Очищает одноразовый код 2FA после успешного входа."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE instagram_profiles
                SET instagram_verification_code = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                """,
                (user_id,),
            )
    except Exception as e:
        logger.warning("clear_instagram_verification_code user_id=%s: %s", user_id, e)
    finally:
        await release_db_connection(conn)


async def set_instagram_auth_error(user_id: int, message: Optional[str]) -> None:
    """Сохраняет текст ошибки входа (challenge, неверный пароль и т.д.)."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE instagram_profiles
                SET instagram_last_auth_error = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                """,
                (message, user_id),
            )
    except Exception as e:
        logger.warning("set_instagram_auth_error user_id=%s: %s", user_id, e)
    finally:
        await release_db_connection(conn)
