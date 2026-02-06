"""Сервис для управления постами."""

import json
from typing import Dict, List, Optional
from database import get_db_connection, release_db_connection


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
            await release_db_connection(conn)

    async def create_wp_post_record(
        self,
        user_id: int,
        text: str,
        title: Optional[str] = None,
    ) -> Dict:
        """Создает пост WordPress в таблице wp_posts.
        
        Args:
            user_id: ID пользователя
            text: Текст поста (HTML, до 150000 символов)
            title: Заголовок поста
        
        Returns:
            Созданный пост из таблицы wp_posts
        """
        # Проверка лимита символов для WordPress
        limit = self.PLATFORM_LIMITS.get("wp", 150000)
        if len(text) > limit:
            raise ValueError(f"Text exceeds wp limit of {limit} characters")
        
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO wp_posts (
                        user_id, post_text, title, domain, url, author, avatar,
                        post_date, screenshot, images, image_over_text,
                        comments, reposts, likes, views, is_ad, status,
                        post_type, to_tg, to_tw, to_wp, to_vk
                    ) VALUES (
                        %s, %s, %s, NULL, NULL, NULL, NULL,
                        NULL, NULL, '[]', NULL,
                        0, 0, 0, 0, FALSE, 'collected',
                        'wp', FALSE, FALSE, TRUE, FALSE
                    )
                    RETURNING *
                    """,
                    (
                        user_id,
                        text,
                        title,
                    )
                )
                row = await cur.fetchone()
                return self._row_to_post(row, cur.description)
        finally:
            await release_db_connection(conn)

    async def create_tg_post_record(
        self,
        user_id: int,
        text: str,
        images: Optional[List[str]] = None,
    ) -> Dict:
        """Создает пост Telegram в таблице tg_posts.
        
        Args:
            user_id: ID пользователя
            text: Текст поста (до 4096 символов)
            images: Список URL изображений
        
        Returns:
            Созданный пост из таблицы tg_posts
        """
        # Проверка лимита символов для Telegram
        limit = self.PLATFORM_LIMITS.get("tg", 4096)
        if len(text) > limit:
            raise ValueError(f"Text exceeds tg limit of {limit} characters")
        
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO tg_posts (
                        user_id, post_text, title, domain, url, author, avatar,
                        post_date, screenshot, images, image_over_text,
                        comments, reposts, likes, views, is_ad, status,
                        post_type, to_tg, to_tw, to_wp, to_vk
                    ) VALUES (
                        %s, %s, NULL, NULL, NULL, NULL, NULL,
                        NULL, NULL, %s, NULL,
                        0, 0, 0, 0, FALSE, 'collected',
                        'tg', TRUE, FALSE, FALSE, FALSE
                    )
                    RETURNING *
                    """,
                    (
                        user_id,
                        text,
                        json.dumps(images or []),
                    )
                )
                row = await cur.fetchone()
                return self._row_to_post(row, cur.description)
        finally:
            await release_db_connection(conn)
    
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
            await release_db_connection(conn)

    async def get_wp_posts(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Получает посты WordPress пользователя из таблицы wp_posts.
        
        Args:
            user_id: ID пользователя
            limit: Лимит записей
            offset: Смещение
        
        Returns:
            Список постов WordPress
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT *
                    FROM wp_posts
                    WHERE user_id = %s AND (status IS NULL OR status != 'deleted')
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (user_id, limit, offset)
                )
                rows = await cur.fetchall()
                return [self._row_to_post(row, cur.description) for row in rows]
        finally:
            await release_db_connection(conn)

    async def get_wp_post(self, user_id: int, post_id: int) -> Optional[Dict]:
        """Получает один пост WordPress по id.

        Args:
            user_id: ID пользователя
            post_id: ID поста

        Returns:
            Пост или None
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT * FROM wp_posts
                    WHERE user_id = %s AND id = %s
                    """,
                    (user_id, post_id)
                )
                row = await cur.fetchone()
                if row:
                    return self._row_to_post(row, cur.description)
                return None
        finally:
            await release_db_connection(conn)

    async def update_wp_post(
        self,
        user_id: int,
        post_id: int,
        title: Optional[str] = None,
        post_text: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[Dict]:
        """Обновляет пост WordPress.

        Args:
            user_id: ID пользователя
            post_id: ID поста
            title: Заголовок
            post_text: Текст поста (content)
            status: Статус (draft, publish, pending, private, collected, etc.)

        Returns:
            Обновленный пост или None
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                updates = []
                params = []
                if title is not None:
                    updates.append("title = %s")
                    params.append(title)
                if post_text is not None:
                    updates.append("post_text = %s")
                    params.append(post_text)
                if status is not None:
                    updates.append("status = %s")
                    params.append(status)
                if not updates:
                    return await self.get_wp_post(user_id, post_id)
                params.extend([user_id, post_id])
                await cur.execute(
                    f"""
                    UPDATE wp_posts SET {", ".join(updates)}, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s AND id = %s
                    RETURNING *
                    """,
                    params
                )
                row = await cur.fetchone()
                if row:
                    return self._row_to_post(row, cur.description)
                return None
        finally:
            await release_db_connection(conn)

    async def delete_wp_post(self, user_id: int, post_id: int) -> Optional[Dict]:
        """Помечает пост WordPress как удаленный (status = 'deleted').

        Args:
            user_id: ID пользователя
            post_id: ID поста

        Returns:
            Обновленный пост или None
        """
        return await self.update_wp_post(user_id, post_id, status="deleted")

    async def get_tg_posts(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Получает посты Telegram пользователя из таблицы tg_posts.
        
        Args:
            user_id: ID пользователя
            limit: Лимит записей
            offset: Смещение
        
        Returns:
            Список постов Telegram
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT *
                    FROM tg_posts
                    WHERE user_id = %s AND (status IS NULL OR status != 'deleted')
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (user_id, limit, offset)
                )
                rows = await cur.fetchall()
                return [self._row_to_post(row, cur.description) for row in rows]
        finally:
            await release_db_connection(conn)

    async def get_tg_post(self, user_id: int, post_id: int) -> Optional[Dict]:
        """Получает один пост Telegram по id.

        Args:
            user_id: ID пользователя
            post_id: ID поста

        Returns:
            Пост или None
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT * FROM tg_posts
                    WHERE user_id = %s AND id = %s
                    """,
                    (user_id, post_id)
                )
                row = await cur.fetchone()
                if row:
                    return self._row_to_post(row, cur.description)
                return None
        finally:
            await release_db_connection(conn)

    async def update_tg_post(
        self,
        user_id: int,
        post_id: int,
        text: Optional[str] = None,
        images: Optional[List[str]] = None,
        status: Optional[str] = None,
    ) -> Optional[Dict]:
        """Обновляет пост Telegram.

        Args:
            user_id: ID пользователя
            post_id: ID поста
            text: Текст поста
            images: Список URL изображений
            status: Статус (collected, processed, published, deleted, etc.)

        Returns:
            Обновленный пост или None
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                updates = []
                params = []
                if text is not None:
                    # Проверка лимита символов для Telegram
                    limit = self.PLATFORM_LIMITS.get("tg", 4096)
                    if len(text) > limit:
                        raise ValueError(f"Text exceeds tg limit of {limit} characters")
                    updates.append("post_text = %s")
                    params.append(text)
                if images is not None:
                    updates.append("images = %s")
                    params.append(json.dumps(images))
                if status is not None:
                    updates.append("status = %s")
                    params.append(status)
                if not updates:
                    return await self.get_tg_post(user_id, post_id)
                params.extend([user_id, post_id])
                await cur.execute(
                    f"""
                    UPDATE tg_posts SET {", ".join(updates)}, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s AND id = %s
                    RETURNING *
                    """,
                    params
                )
                row = await cur.fetchone()
                if row:
                    return self._row_to_post(row, cur.description)
                return None
        finally:
            await release_db_connection(conn)

    async def delete_tg_post(self, user_id: int, post_id: int) -> Optional[Dict]:
        """Помечает пост Telegram как удаленный (status = 'deleted').

        Args:
            user_id: ID пользователя
            post_id: ID поста

        Returns:
            Обновленный пост или None
        """
        return await self.update_tg_post(user_id, post_id, status="deleted")
    
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
            await release_db_connection(conn)
    
    def _row_to_post(self, row, description) -> Dict:
        """Преобразует строку БД в словарь поста."""
        columns = [col.name for col in description]
        post = dict(zip(columns, row))
        if isinstance(post.get("images"), str):
            post["images"] = json.loads(post["images"])
        return post


post_service = PostService()
