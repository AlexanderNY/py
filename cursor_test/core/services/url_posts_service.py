"""Сервис сохранения постов из url-bot в таблицу url_posts."""

import base64
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from database import get_db_connection, release_db_connection

logger = logging.getLogger(__name__)

# Каталог для сохранения скриншотов url (относительно cwd Core)
UPLOADS_URL_DIR = "uploads/url"


def _save_screenshot_from_base64(screenshot_base64: str, user_id: int) -> str | None:
    """Декодирует base64, сохраняет в uploads/url/{user_id}/{date}/{uuid}.jpg. Возвращает относительный путь."""
    if not screenshot_base64:
        return None
    try:
        data = base64.b64decode(screenshot_base64, validate=True)
    except Exception as e:
        logger.warning("Invalid screenshot base64: %s", e)
        return None
    if not data:
        return None
    try:
        date_part = datetime.utcnow().strftime("%Y-%m-%d")
        dir_path = Path(UPLOADS_URL_DIR) / str(user_id) / date_part
        dir_path.mkdir(parents=True, exist_ok=True)
        name = f"{uuid.uuid4().hex}.jpg"
        file_path = dir_path / name
        file_path.write_bytes(data)
        return f"/uploads/url/{user_id}/{date_part}/{name}"
    except Exception as e:
        logger.warning("Screenshot save failed: %s", e)
        return None


async def save_url_post(item: dict[str, Any]) -> int | None:
    """
    Сохраняет один пост из url-bot в url_posts.

    Если передан screenshot_base64 — сохраняет файл в uploads/url/... и в images кладёт путь.
    Если передан screenshot_path — в images кладёт путь как есть (файл уже сохранён url-bot).

    Returns:
        id вставленной записи или None при ошибке.
    """
    user_id = item.get("user_id")
    url = item.get("url") or ""
    post_text = item.get("post_text") or ""
    to_tg = item.get("to_tg", False)
    to_tw = item.get("to_tw", False)
    to_wp = item.get("to_wp", False)
    to_vk = item.get("to_vk", False)

    images: list[str] = []
    if item.get("screenshot_path"):
        images.append(item["screenshot_path"])
    elif item.get("screenshot_base64"):
        path = _save_screenshot_from_base64(item["screenshot_base64"], user_id)
        if path:
            images.append(path)

    post_date = datetime.utcnow()
    status = "collected"
    images_json = json.dumps(images, ensure_ascii=False)

    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO url_posts (
                    user_id, url, post_text, post_date, images, status,
                    to_tg, to_tw, to_wp, to_vk
                ) VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    user_id,
                    url,
                    post_text,
                    post_date,
                    images_json,
                    status,
                    to_tg,
                    to_tw,
                    to_wp,
                    to_vk,
                ),
            )
            row = await cur.fetchone()
            url_post_id = row[0] if row else None
            if url_post_id is None:
                return None

            # Дублируем пост в общую таблицу posts для обработки по общим правилам (processor и т.д.)
            await cur.execute(
                """
                INSERT INTO posts (
                    user_id, domain, url, title, author, avatar, post_date, post_text,
                    screenshot, images, image_over_text, comments, reposts, likes, views,
                    is_ad, status, post_type, to_tg, to_tw, to_wp, to_vk,
                    source_platform, source_id
                ) VALUES (
                    %s, NULL, %s, NULL, NULL, NULL, %s, %s, NULL, %s::jsonb, NULL,
                    0, 0, 0, 0, FALSE, 'collected', NULL, %s, %s, %s, %s,
                    'url', %s
                )
                ON CONFLICT (source_platform, source_id)
                    WHERE source_platform IS NOT NULL
                DO NOTHING
                """,
                (
                    user_id,
                    url,
                    post_date,
                    post_text,
                    images_json,
                    to_tg,
                    to_tw,
                    to_wp,
                    to_vk,
                    url_post_id,
                ),
            )

            # Помечаем запись в url_posts как переданную в posts (чтобы collector не копировал повторно)
            await cur.execute(
                """
                UPDATE url_posts
                SET status = 'processing', updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (url_post_id,),
            )

            return url_post_id
    except Exception as e:
        logger.exception("Save url post failed: %s", e)
        return None
    finally:
        await release_db_connection(conn)


async def save_url_posts_batch(items: list[dict[str, Any]]) -> list[int]:
    """Сохраняет несколько постов из url-bot. Возвращает список id вставленных записей."""
    ids: list[int] = []
    for item in items:
        post_id = await save_url_post(item)
        if post_id is not None:
            ids.append(post_id)
    return ids
