"""Публикация постов со статусом ready в channel_to_post."""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional
from database import get_db_connection, release_db_connection
from config import settings
from .client_manager import TelegramClientManager


logger = logging.getLogger(__name__)

TG_MESSAGE_LIMIT = 4096


def _log_action(msg: str, *args, **kwargs) -> None:
    if settings.LOG_BOT_ACTIONS:
        logger.info(msg, *args, **kwargs)
    else:
        logger.debug(msg, *args, **kwargs)


class PostPublisher:
    """Сервис публикации постов из tg_posts в Telegram канал."""

    def __init__(self, client_manager: TelegramClientManager):
        self.client_manager = client_manager

    async def get_ready_posts(self) -> List[Dict]:
        """Получает посты со статусом ready с channel_to_post из tg_profiles."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT p.id, p.user_id, p.post_text, p.images, p.status,
                           pr.channel_to_post
                    FROM tg_posts p
                    JOIN tg_profiles pr ON p.user_id = pr.user_id
                    WHERE p.status = 'ready'
                      AND pr.channel_to_post IS NOT NULL
                      AND pr.channel_to_post != ''
                    ORDER BY p.created_at ASC
                    """
                )
                rows = await cur.fetchall()
                columns = [col.name for col in cur.description]
                return [dict(zip(columns, row)) for row in rows]
        finally:
            await release_db_connection(conn)

    def _resolve_image_path(self, image_path: str) -> Optional[str]:
        """Преобразует относительный путь изображения в абсолютный."""
        if not image_path:
            return None
        path = image_path.lstrip("/")
        base = settings.PATH_TO_TG_IMAGE or os.getcwd()
        full_path = os.path.join(base, path) if path else os.path.join(base, image_path)
        if os.path.exists(full_path):
            return os.path.abspath(full_path)
        if os.path.exists(image_path):
            return os.path.abspath(image_path)
        return None

    def _get_first_image_path(self, images_raw) -> Optional[str]:
        """Извлекает путь к первому изображению из images JSONB."""
        if not images_raw:
            return None
        try:
            images = json.loads(images_raw) if isinstance(images_raw, str) else images_raw
            if isinstance(images, list) and images:
                first = images[0]
                path = first if isinstance(first, str) else first.get("path", first)
                return self._resolve_image_path(str(path))
        except (json.JSONDecodeError, TypeError):
            pass
        return None

    def _parse_channel_to_post(self, channel: str):
        """Преобразует channel_to_post в формат для send_message."""
        if not channel:
            return None
        channel = str(channel).strip()
        if channel.startswith("@"):
            return channel
        try:
            return int(channel)
        except ValueError:
            return channel

    async def publish_post(self, post: Dict) -> bool:
        """Публикует один пост в канал.

        Args:
            post: Словарь с данными поста (id, user_id, post_text, images, channel_to_post)

        Returns:
            True при успешной публикации, False иначе
        """
        post_id = post.get("id")
        user_id = post.get("user_id")
        text = post.get("post_text") or ""
        channel = self._parse_channel_to_post(post.get("channel_to_post"))

        if not channel:
            logger.warning(f"Post {post_id}: channel_to_post is empty for user {user_id}")
            return False

        client = self.client_manager.get_client(user_id)
        if not client:
            logger.warning(f"Post {post_id}: no active client for user {user_id}")
            return False

        image_path = self._get_first_image_path(post.get("images"))

        try:
            if len(text) >= TG_MESSAGE_LIMIT:
                text = text[: TG_MESSAGE_LIMIT - 3] + "..."
                image_path = None

            if image_path:
                await client.send_message(channel, text, file=image_path)
            else:
                await client.send_message(channel, text)

            await self._update_post_status(post_id, "published")
            _log_action("Published post %s to %s for user %s", post_id, channel, user_id)
            return True

        except Exception as e:
            logger.error(f"Error publishing post {post_id}: {e}", exc_info=True)
            return False

    async def _update_post_status(self, post_id: int, status: str) -> None:
        """Обновляет статус поста в tg_posts."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE tg_posts
                    SET status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (status, post_id),
                )
        finally:
            await release_db_connection(conn)

    async def publish_ready_posts(self) -> int:
        """Публикует все посты со статусом ready.

        Returns:
            Количество успешно опубликованных постов
        """
        posts = await self.get_ready_posts()
        _log_action("get_ready_posts returned %d posts", len(posts))
        if not posts:
            return 0

        published = 0
        for post in posts:
            if await self.publish_post(post):
                published += 1
            await asyncio.sleep(20)

        _log_action("publish_ready_posts: published %d of %d", published, len(posts))
        return published
