"""Публикация постов из vk_posts со статусом ready в group_to_post."""

import asyncio
import logging
from typing import Dict, List, Optional

from database import get_db_connection, release_db_connection
from config import settings
from .vk_client import VkClient


logger = logging.getLogger(__name__)

VK_MESSAGE_LIMIT = 16384


def _log_action(msg: str, *args, **kwargs) -> None:
    if settings.LOG_BOT_ACTIONS:
        logger.info(msg, *args, **kwargs)
    else:
        logger.debug(msg, *args, **kwargs)


def _parse_group_to_post(value: Optional[str]) -> Optional[int]:
    """Преобразует group_to_post в owner_id (отрицательное число)."""
    if not value or not str(value).strip():
        return None
    s = str(value).strip()
    try:
        n = int(s)
        return -abs(n)
    except ValueError:
        return None


class PostPublisher:
    """Публикация постов из vk_posts в группу VK."""

    async def get_ready_posts(self) -> List[Dict]:
        """Посты со статусом ready и непустым group_to_post, access_token."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT p.id, p.user_id, p.post_text, p.images,
                           pr.group_to_post, pr.access_token, pr.from_group
                    FROM vk_posts p
                    JOIN vk_profiles pr ON p.user_id = pr.user_id
                    WHERE p.status = 'ready'
                      AND pr.group_to_post IS NOT NULL
                      AND pr.group_to_post != ''
                      AND pr.access_token IS NOT NULL
                      AND pr.access_token != ''
                    ORDER BY p.created_at ASC
                    """
                )
                rows = await cur.fetchall()
                cols = [c.name for c in cur.description]
                return [dict(zip(cols, row)) for row in rows]
        finally:
            await release_db_connection(conn)

    async def publish_post(self, post: Dict) -> bool:
        """Публикует один пост в группу. post: id, user_id, post_text, images, group_to_post, access_token, from_group."""
        post_id = post.get("id")
        user_id = post.get("user_id")
        text = (post.get("post_text") or "")[:VK_MESSAGE_LIMIT]
        owner_id = _parse_group_to_post(post.get("group_to_post"))
        token = post.get("access_token")
        from_group = bool(post.get("from_group", True))

        if not owner_id or not token:
            logger.warning("Post %s: missing group_to_post or access_token", post_id)
            return False

        client = VkClient(token)
        new_post_id = await client.wall_post(
            owner_id=owner_id,
            message=text,
            from_group=from_group,
            attachments=None,
        )
        if new_post_id is None:
            return False
        await self._update_post_status(post_id, "published")
        _log_action("Published vk post %s to group %s for user %s", post_id, owner_id, user_id)
        return True

    async def _update_post_status(self, post_id: int, status: str) -> None:
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE vk_posts
                    SET status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (status, post_id),
                )
        finally:
            await release_db_connection(conn)

    async def publish_ready_posts(self) -> int:
        """Публикует все посты со статусом ready. Возвращает количество опубликованных."""
        posts = await self.get_ready_posts()
        _log_action("get_ready_posts returned %d posts", len(posts))
        if not posts:
            return 0
        published = 0
        for post in posts:
            if await self.publish_post(post):
                published += 1
            await asyncio.sleep(2)
        _log_action("publish_ready_posts: published %d of %d", published, len(posts))
        return published
