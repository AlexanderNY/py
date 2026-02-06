"""Сбор и сохранение постов в БД."""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from telethon import events
from database import get_db_connection, release_db_connection


logger = logging.getLogger(__name__)


class PostCollector:
    """Сервис для сохранения постов в БД."""
    
    async def save_post(
        self,
        user_id: int,
        event: events.NewMessage.Event,
        images: List[str],
        profile: Dict
    ) -> Optional[Dict]:
        """Сохраняет пост в таблицу posts.
        
        Args:
            user_id: ID пользователя
            event: Событие нового сообщения
            images: Список путей к изображениям
            profile: Профиль пользователя из БД
            
        Returns:
            Словарь с данными сохраненного поста или None в случае ошибки
        """
        try:
            # Извлекаем данные из сообщения
            sender = await event.get_sender()
            message = event.message
            
            # Формируем данные для сохранения
            post_text = message.message or ""
            post_date = message.date
            author = None
            author_id = None
            
            if sender:
                author = getattr(sender, 'title', None) or getattr(sender, 'username', None)
                author_id = sender.id
            
            # Определяем to_tg на основе publish_enabled
            to_tg = profile.get('publish_enabled', False)
            
            # Сохраняем в БД
            conn = await get_db_connection()
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO posts (
                            user_id, post_text, post_date, author,
                            images, status, post_type, to_tg,
                            created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s,
                            %s, %s, %s, %s,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                        RETURNING *
                        """,
                        (
                            user_id,
                            post_text,
                            post_date,
                            author,
                            json.dumps(images),
                            'ready',
                            'tg',
                            to_tg,
                        )
                    )
                    
                    row = await cur.fetchone()
                    if row:
                        # Преобразуем строку в словарь
                        columns = [col.name for col in cur.description]
                        post = dict(zip(columns, row))
                        
                        # Парсим JSONB поля
                        if isinstance(post.get('images'), str):
                            try:
                                post['images'] = json.loads(post['images'])
                            except (json.JSONDecodeError, TypeError):
                                post['images'] = []
                        
                        logger.info(f"Saved post {post['id']} for user {user_id}")
                        return post
                    
            finally:
                await release_db_connection(conn)
        
        except Exception as e:
            logger.error(f"Error saving post for user {user_id}: {e}", exc_info=True)
            return None
