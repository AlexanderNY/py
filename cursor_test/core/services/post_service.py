"""Сервис для управления постами."""

import json
from typing import Dict, List, Optional
from database import get_db_connection


class PostService:
    """Сервис для создания и управления постами."""
    
    # Лимиты символов для разных платформ
    PLATFORM_LIMITS = {
        "tg": 4096,
        "tw": 280,
        "wp": 150000,
        "vk": 15985,
        "cpost": 150000,
    }
    
    async def create_post(
        self,
        user_id: int,
        text: str,
        platform: str,
        title: Optional[str] = None,
        to_tg: bool = False,
        to_tw: bool = False,
        to_wp: bool = False,
        to_vk: bool = False,
        **kwargs
    ) -> Dict:
        """Создает новый пост.
        
        Args:
            user_id: ID пользователя
            text: Текст поста
            platform: Исходная платформа (tg, tw, wp, vk, cpost)
            title: Заголовок поста (опционально)
            to_tg: Отправлять в Telegram
            to_tw: Отправлять в Twitter
            to_wp: Отправлять в WordPress
            to_vk: Отправлять в VKontakte
            **kwargs: Дополнительные поля поста
            
        Returns:
            Созданный пост
            
        Raises:
            ValueError: Если текст превышает лимит платформы
        """
        # Проверка лимита символов
        limit = self.PLATFORM_LIMITS.get(platform, 150000)
        if len(text) > limit:
            raise ValueError(f"Text exceeds {platform} limit of {limit} characters")
        
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO posts (
                        user_id, post_text, title, domain, url, author, avatar,
                        post_date, screenshot, images, image_over_text,
                        comments, reposts, likes, views, is_ad, status,
                        post_type, to_tg, to_tw, to_wp, to_vk
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                    RETURNING *
                    """,
                    (
                        user_id,
                        text,
                        title,
                        kwargs.get("domain"),
                        kwargs.get("url"),
                        kwargs.get("author"),
                        kwargs.get("avatar"),
                        kwargs.get("post_date"),
                        kwargs.get("screenshot"),
                        json.dumps(kwargs.get("images", [])),
                        kwargs.get("image_over_text"),
                        kwargs.get("comments", 0),
                        kwargs.get("reposts", 0),
                        kwargs.get("likes", 0),
                        kwargs.get("views", 0),
                        kwargs.get("is_ad", False),
                        "collected",
                        platform,
                        to_tg,
                        to_tw,
                        to_wp,
                        to_vk,
                    )
                )
                row = await cur.fetchone()
                return self._row_to_post(row, cur.description)
        finally:
            conn.close()
    
    async def get_posts(
        self,
        user_id: int,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Получает посты пользователя.
        
        Args:
            user_id: ID пользователя
            status: Фильтр по статусу
            platform: Фильтр по платформе
            limit: Лимит записей
            offset: Смещение
            
        Returns:
            Список постов
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                query = "SELECT * FROM posts WHERE user_id = %s"
                params = [user_id]
                
                if status:
                    query += " AND status = %s"
                    params.append(status)
                
                if platform:
                    field_map = {
                        "tg": "to_tg",
                        "tw": "to_tw",
                        "wp": "to_wp",
                        "vk": "to_vk",
                    }
                    if platform in field_map:
                        query += f" AND {field_map[platform]} = TRUE"
                
                query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                await cur.execute(query, params)
                rows = await cur.fetchall()
                
                return [self._row_to_post(row, cur.description) for row in rows]
        finally:
            conn.close()
    
    async def update_post_status(self, post_id: int, status: str) -> Optional[Dict]:
        """Обновляет статус поста.
        
        Args:
            post_id: ID поста
            status: Новый статус (collected, processed, published)
            
        Returns:
            Обновленный пост или None
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE posts SET status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING *
                    """,
                    (status, post_id)
                )
                row = await cur.fetchone()
                if row:
                    return self._row_to_post(row, cur.description)
                return None
        finally:
            conn.close()
    
    def _row_to_post(self, row, description) -> Dict:
        """Преобразует строку БД в словарь поста."""
        columns = [col.name for col in description]
        post = dict(zip(columns, row))
        if isinstance(post.get("images"), str):
            post["images"] = json.loads(post["images"])
        return post


post_service = PostService()
