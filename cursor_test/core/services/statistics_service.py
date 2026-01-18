"""Сервис для сбора статистики постов."""

from typing import List, Dict
from database import get_db_connection


class StatisticsService:
    """Сервис для получения статистики по постам."""
    
    async def get_statistics(self) -> List[Dict]:
        """Собирает статистику по постам для каждой платформы.
        
        Returns:
            Список статистики по платформам
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                # Статистика для Telegram
                tg_stats = await self._get_platform_stats(cur, "to_tg", "Telegram")
                
                # Статистика для Twitter
                tw_stats = await self._get_platform_stats(cur, "to_tw", "Twitter")
                
                # Статистика для WordPress
                wp_stats = await self._get_platform_stats(cur, "to_wp", "WordPress")
                
                # Статистика для VKontakte
                vk_stats = await self._get_platform_stats(cur, "to_vk", "VKontakte")
                
                # Общая статистика
                total_stats = await self._get_total_stats(cur)
                
                return [tg_stats, tw_stats, wp_stats, vk_stats, total_stats]
        finally:
            conn.close()
    
    async def _get_platform_stats(self, cur, platform_field: str, platform_name: str) -> Dict:
        """Получает статистику для конкретной платформы.
        
        Args:
            cur: Курсор БД
            platform_field: Поле платформы (to_tg, to_tw и т.д.)
            platform_name: Название платформы
            
        Returns:
            Словарь со статистикой
        """
        # Собранные посты
        await cur.execute(f"""
            SELECT COUNT(*) FROM posts 
            WHERE {platform_field} = TRUE AND status = 'collected'
        """)
        collected = (await cur.fetchone())[0]
        
        # Обработанные посты
        await cur.execute(f"""
            SELECT COUNT(*) FROM posts 
            WHERE {platform_field} = TRUE AND status = 'processed'
        """)
        processed = (await cur.fetchone())[0]
        
        # Опубликованные посты
        await cur.execute(f"""
            SELECT COUNT(*) FROM posts 
            WHERE {platform_field} = TRUE AND status = 'published'
        """)
        published = (await cur.fetchone())[0]
        
        return {
            "service_name": platform_name,
            "collected_posts": collected,
            "processed_posts": processed,
            "published_posts": published
        }
    
    async def _get_total_stats(self, cur) -> Dict:
        """Получает общую статистику по всем постам.
        
        Args:
            cur: Курсор БД
            
        Returns:
            Словарь с общей статистикой
        """
        await cur.execute("SELECT COUNT(*) FROM posts WHERE status = 'collected'")
        collected = (await cur.fetchone())[0]
        
        await cur.execute("SELECT COUNT(*) FROM posts WHERE status = 'processed'")
        processed = (await cur.fetchone())[0]
        
        await cur.execute("SELECT COUNT(*) FROM posts WHERE status = 'published'")
        published = (await cur.fetchone())[0]
        
        return {
            "service_name": "Total",
            "collected_posts": collected,
            "processed_posts": processed,
            "published_posts": published
        }


statistics_service = StatisticsService()
