"""Сбор постов из Instagram (свои и usernames_to_read) и сохранение в instagram_posts."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from database import get_db_connection, release_db_connection
from config import settings
from .instagram_client import InstagramClient


logger = logging.getLogger(__name__)


def _log_action(msg: str, *args, **kwargs) -> None:
    if settings.LOG_BOT_ACTIONS:
        logger.info(msg, *args, **kwargs)
    else:
        logger.debug(msg, *args, **kwargs)


class PostCollector:
    """Сбор постов из своего аккаунта и usernames_to_read в instagram_posts."""

    async def get_profiles_for_collect(self) -> List[Dict]:
        """Профили с collect_enabled, username, password и непустым usernames_to_read или для сбора своих."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT user_id, username, password, usernames_to_read
                    FROM instagram_profiles
                    WHERE collect_enabled = TRUE
                      AND username IS NOT NULL
                      AND username != ''
                      AND password IS NOT NULL
                      AND password != ''
                    """
                )
                rows = await cur.fetchall()
                cols = [c.name for c in cur.description]
                result = []
                for row in rows:
                    rec = dict(zip(cols, row))
                    if isinstance(rec.get("usernames_to_read"), str):
                        try:
                            rec["usernames_to_read"] = json.loads(rec["usernames_to_read"])
                        except (json.JSONDecodeError, TypeError):
                            rec["usernames_to_read"] = []
                    if rec.get("usernames_to_read") is None:
                        rec["usernames_to_read"] = []
                    result.append(rec)
                return result
        finally:
            await release_db_connection(conn)

    async def exists_by_source_id(self, user_id: int, domain: str, source_id: str) -> bool:
        """Проверяет, есть ли уже пост с таким instagram_source_id для user_id и domain."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT 1 FROM instagram_posts
                    WHERE user_id = %s AND domain = %s AND instagram_source_id = %s
                    LIMIT 1
                    """,
                    (user_id, domain, str(source_id)),
                )
                row = await cur.fetchone()
                return row is not None
        finally:
            await release_db_connection(conn)

    async def save_post(
        self,
        user_id: int,
        instagram_source_id: str,
        domain: str,
        post_text: str,
        post_date: Optional[datetime],
        author: Optional[str],
        images_json: str,
        comments: int,
        likes: int,
    ) -> bool:
        """Вставляет пост в instagram_posts со статусом collected."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO instagram_posts (
                        user_id, instagram_source_id, domain, post_text, post_date, author,
                        images, comments, likes, status, post_type
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        'collected', 'instagram'
                    )
                    """,
                    (
                        user_id,
                        instagram_source_id,
                        domain,
                        post_text,
                        post_date,
                        author,
                        images_json,
                        comments,
                        likes,
                    ),
                )
                _log_action(
                    "Saved instagram post user_id=%s domain=%s source_id=%s",
                    user_id,
                    domain,
                    instagram_source_id,
                )
                return True
        except Exception as e:
            logger.error("Error saving instagram post: %s", e, exc_info=True)
            return False
        finally:
            await release_db_connection(conn)

    async def run_collect(self) -> int:
        """Собирает посты: свои + по каждому username из usernames_to_read. Возвращает число сохранённых."""
        profiles = await self.get_profiles_for_collect()
        if not profiles:
            return 0
        saved = 0
        for profile in profiles:
            user_id = profile["user_id"]
            username = (profile.get("username") or "").strip()
            password = profile.get("password") or ""
            if not username or not password:
                continue
            usernames_to_read = profile.get("usernames_to_read") or []
            if not isinstance(usernames_to_read, list):
                usernames_to_read = []
            client = InstagramClient(username, password)
            if not await client.login():
                logger.warning("Instagram login failed for user_id=%s", user_id)
                continue
            self_uid = await client.get_self_user_id()
            # Свои посты
            if self_uid:
                medias = await client.user_medias(self_uid, amount=20)
                domain = username
                for m in medias:
                    pk = m.get("pk") or m.get("id")
                    if not pk:
                        continue
                    source_id = str(pk)
                    if await self.exists_by_source_id(user_id, domain, source_id):
                        continue
                    post_date = m.get("taken_at")
                    if isinstance(post_date, datetime):
                        pass
                    elif post_date and hasattr(post_date, "timestamp"):
                        post_date = datetime.utcfromtimestamp(post_date.timestamp())
                    else:
                        post_date = None
                    ok = await self.save_post(
                        user_id=user_id,
                        instagram_source_id=source_id,
                        domain=domain,
                        post_text=(m.get("caption") or "")[:2200],
                        post_date=post_date,
                        author=username,
                        images_json=json.dumps(m.get("images") or []),
                        comments=m.get("comment_count") or 0,
                        likes=m.get("like_count") or 0,
                    )
                    if ok:
                        saved += 1
            # Посты других аккаунтов
            for uname in usernames_to_read:
                if not uname or not str(uname).strip():
                    continue
                uname = str(uname).strip()
                uid = await client.user_id_from_username(uname)
                if uid is None:
                    continue
                medias = await client.user_medias(uid, amount=20)
                domain = uname
                for m in medias:
                    pk = m.get("pk") or m.get("id")
                    if not pk:
                        continue
                    source_id = str(pk)
                    if await self.exists_by_source_id(user_id, domain, source_id):
                        continue
                    post_date = m.get("taken_at")
                    if isinstance(post_date, datetime):
                        pass
                    elif post_date and hasattr(post_date, "timestamp"):
                        post_date = datetime.utcfromtimestamp(post_date.timestamp())
                    else:
                        post_date = None
                    ok = await self.save_post(
                        user_id=user_id,
                        instagram_source_id=source_id,
                        domain=domain,
                        post_text=(m.get("caption") or "")[:2200],
                        post_date=post_date,
                        author=uname,
                        images_json=json.dumps(m.get("images") or []),
                        comments=m.get("comment_count") or 0,
                        likes=m.get("like_count") or 0,
                    )
                    if ok:
                        saved += 1
        return saved
