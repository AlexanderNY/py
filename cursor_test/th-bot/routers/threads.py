"""Роуты Threads: auth status, auth url, reload, schedule."""

import json
import logging
from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from services.threads_service import (
    get_auth_status,
    build_oauth_url,
    get_pending_posts_for_user,
    set_post_status,
    verify_threads_auth,
)
from services.publish_service import publish_text_post, publish_image_post

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/threads", tags=["Threads"])


def _get_user_id(x_user_id: Optional[str] = Header(None)) -> int:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")


@router.get("/auth/status/{user_id}")
async def auth_status(user_id: int):
    """Статус OAuth: connected, expires_at."""
    return await get_auth_status(user_id)


@router.get("/auth/verify/{user_id}")
async def auth_verify(user_id: int):
    """Проверка токена у Meta (debug_token или GET /me)."""
    return await verify_threads_auth(user_id)


@router.get("/auth/url")
async def auth_url(x_user_id: Optional[str] = Header(None)):
    """URL для редиректа пользователя на Meta OAuth (state = user_id)."""
    user_id = _get_user_id(x_user_id)
    url = build_oauth_url(user_id)
    if not url:
        raise HTTPException(
            status_code=503,
            detail="OAuth not configured (META_APP_ID, THREADS_OAUTH_REDIRECT_URI)",
        )
    return {"url": url}


@router.post("/reload")
async def reload():
    """Перезагрузка (заглушка: профили читаются из БД по запросу)."""
    return {"status": "ok", "message": "Reload done"}


@router.post("/schedule")
async def schedule():
    """
    Один проход: для каждого пользователя с publish_enabled и токеном
    забираем посты из threads_posts и публикуем в Threads API.
    """
    from database import get_db_connection, release_db_connection

    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT user_id, access_token, threads_user_id
                FROM threads_profiles
                WHERE publish_enabled = TRUE AND access_token IS NOT NULL AND access_token != ''
                """
            )
            rows = await cur.fetchall()
    finally:
        release_db_connection(conn)

    published = 0
    errors = 0
    for (user_id, access_token, threads_user_id) in rows:
        if not threads_user_id:
            logger.warning("user_id=%s: threads_user_id not set, skip publish", user_id)
            continue
        posts = await get_pending_posts_for_user(user_id, limit=5)
        for post in posts:
            post_id = post["id"]
            text = (post.get("post_text") or "").strip()
            raw_images = post.get("images") or []
            images = raw_images if isinstance(raw_images, list) else (json.loads(raw_images) if isinstance(raw_images, str) else [])
            if not text:
                await set_post_status(user_id, post_id, "skipped")
                continue
            if images:
                # Публикуем с первым изображением (URL должен быть абсолютным и доступным для Meta)
                img_url = images[0] if isinstance(images[0], str) else images[0]
                result = await publish_image_post(
                    threads_user_id, access_token, text, img_url
                )
            else:
                result = await publish_text_post(threads_user_id, access_token, text)
            if result:
                await set_post_status(user_id, post_id, "published")
                published += 1
            else:
                await set_post_status(user_id, post_id, "failed")
                errors += 1

    return {"status": "ok", "published": published, "errors": errors}
