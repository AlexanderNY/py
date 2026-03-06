"""Сервис для OAuth URL и статуса Threads (профили в БД)."""

import json
import logging
from typing import Optional

from config import settings
from database import get_db_connection, release_db_connection

logger = logging.getLogger(__name__)

META_OAUTH_BASE = "https://www.facebook.com/v18.0/dialog/oauth"


async def get_threads_profile(user_id: int) -> Optional[dict]:
    """Читает профиль Threads из БД (включая access_token для бота)."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT user_id, access_token, token_expires_at, threads_user_id,
                       publish_enabled, schedule_type, time_intervals
                FROM threads_profiles
                WHERE user_id = %s
                """,
                (user_id,),
            )
            row = await cur.fetchone()
            if not row:
                return None
            desc = [c.name for c in cur.description]
            return dict(zip(desc, row))
    finally:
        release_db_connection(conn)


async def get_auth_status(user_id: int) -> dict:
    """Возвращает статус OAuth: connected, expires_at (без токена)."""
    profile = await get_threads_profile(user_id)
    if not profile:
        return {"user_id": user_id, "connected": False, "message": "Profile not found"}
    has_token = bool(profile.get("access_token"))
    expires_at = profile.get("token_expires_at")
    return {
        "user_id": user_id,
        "connected": has_token,
        "expires_at": expires_at.isoformat() if expires_at else None,
        "message": "Connected" if has_token else "Not connected",
    }


def build_oauth_url(user_id: int) -> str:
    """Собирает URL для редиректа пользователя на Meta OAuth (state = user_id)."""
    app_id = (settings.META_APP_ID or "").strip()
    redirect_uri = (settings.THREADS_OAUTH_REDIRECT_URI or "").strip()
    scope = (settings.THREADS_OAUTH_SCOPE or "threads_basic,threads_content_publish").strip()
    if not app_id or not redirect_uri:
        return ""
    from urllib.parse import urlencode
    params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": str(user_id),
        "response_type": "code",
    }
    return f"{META_OAUTH_BASE}?{urlencode(params)}"


async def get_pending_posts_for_user(user_id: int, limit: int = 10) -> list:
    """Посты пользователя со статусом collected/ready к публикации в Threads."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id, user_id, post_text, images, status
                FROM threads_posts
                WHERE user_id = %s AND status NOT IN ('deleted', 'published')
                ORDER BY created_at ASC
                LIMIT %s
                """,
                (user_id, limit),
            )
            rows = await cur.fetchall()
            desc = [c.name for c in cur.description]
            return [dict(zip(desc, row)) for row in rows]
    finally:
        release_db_connection(conn)


async def set_post_status(user_id: int, post_id: int, status: str) -> None:
    """Обновляет статус поста (например published или failed)."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE threads_posts SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s AND id = %s",
                (status, user_id, post_id),
            )
    finally:
        release_db_connection(conn)
