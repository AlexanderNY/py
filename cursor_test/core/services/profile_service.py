"""Сервис для управления профилями пользователей."""

import json
from typing import Optional, Dict, Any
from database import get_db_connection


class ProfileService:
    """Сервис для CRUD операций с профилями всех платформ."""
    
    # ==================== Telegram ====================
    
    async def get_tg_profile(self, user_id: int) -> Optional[Dict]:
        """Получает профиль Telegram пользователя."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM tg_profiles WHERE user_id = %s",
                    (user_id,)
                )
                row = await cur.fetchone()
                if row:
                    return self._row_to_tg_profile(row, cur.description)
                return None
        finally:
            conn.close()
    
    async def save_tg_profile(self, user_id: int, data: Dict) -> Dict:
        """Сохраняет или обновляет профиль Telegram."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO tg_profiles (
                        user_id, publish_enabled, collect_enabled, schedule_type,
                        time_intervals, api_id, api_hash, chats_to_read,
                        save_conditions, channel_to_post, process_enabled,
                        processing_description
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        publish_enabled = EXCLUDED.publish_enabled,
                        collect_enabled = EXCLUDED.collect_enabled,
                        schedule_type = EXCLUDED.schedule_type,
                        time_intervals = EXCLUDED.time_intervals,
                        api_id = EXCLUDED.api_id,
                        api_hash = EXCLUDED.api_hash,
                        chats_to_read = EXCLUDED.chats_to_read,
                        save_conditions = EXCLUDED.save_conditions,
                        channel_to_post = EXCLUDED.channel_to_post,
                        process_enabled = EXCLUDED.process_enabled,
                        processing_description = EXCLUDED.processing_description,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING *
                    """,
                    (
                        user_id,
                        data.get("publish_enabled", False),
                        data.get("collect_enabled", False),
                        data.get("schedule_type", "immediate"),
                        json.dumps(data.get("time_intervals", [])),
                        data.get("api_id"),
                        data.get("api_hash"),
                        json.dumps(data.get("chats_to_read", [])),
                        json.dumps(data.get("save_conditions", [])),
                        data.get("channel_to_post"),
                        data.get("process_enabled", False),
                        data.get("processing_description"),
                    )
                )
                row = await cur.fetchone()
                return self._row_to_tg_profile(row, cur.description)
        finally:
            conn.close()
    
    def _row_to_tg_profile(self, row, description) -> Dict:
        """Преобразует строку БД в словарь профиля Telegram."""
        columns = [col.name for col in description]
        profile = dict(zip(columns, row))
        # Парсим JSON поля
        if isinstance(profile.get("time_intervals"), str):
            profile["time_intervals"] = json.loads(profile["time_intervals"])
        if isinstance(profile.get("chats_to_read"), str):
            profile["chats_to_read"] = json.loads(profile["chats_to_read"])
        if isinstance(profile.get("save_conditions"), str):
            profile["save_conditions"] = json.loads(profile["save_conditions"])
        return profile
    
    # ==================== Twitter ====================
    
    async def get_tw_profile(self, user_id: int) -> Optional[Dict]:
        """Получает профиль Twitter пользователя."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM tw_profiles WHERE user_id = %s",
                    (user_id,)
                )
                row = await cur.fetchone()
                if row:
                    return self._row_to_tw_profile(row, cur.description)
                return None
        finally:
            conn.close()
    
    async def save_tw_profile(self, user_id: int, data: Dict) -> Dict:
        """Сохраняет или обновляет профиль Twitter."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO tw_profiles (
                        user_id, publish_enabled, collect_enabled, schedule_type,
                        time_intervals, use_proxy, proxy_user, proxy_pass,
                        proxy_host, proxy_port, twitter_username, twitter_password
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        publish_enabled = EXCLUDED.publish_enabled,
                        collect_enabled = EXCLUDED.collect_enabled,
                        schedule_type = EXCLUDED.schedule_type,
                        time_intervals = EXCLUDED.time_intervals,
                        use_proxy = EXCLUDED.use_proxy,
                        proxy_user = EXCLUDED.proxy_user,
                        proxy_pass = EXCLUDED.proxy_pass,
                        proxy_host = EXCLUDED.proxy_host,
                        proxy_port = EXCLUDED.proxy_port,
                        twitter_username = EXCLUDED.twitter_username,
                        twitter_password = EXCLUDED.twitter_password,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING *
                    """,
                    (
                        user_id,
                        data.get("publish_enabled", False),
                        data.get("collect_enabled", False),
                        data.get("schedule_type", "immediate"),
                        json.dumps(data.get("time_intervals", [])),
                        data.get("use_proxy", False),
                        data.get("proxy_user"),
                        data.get("proxy_pass"),
                        data.get("proxy_host"),
                        data.get("proxy_port"),
                        data.get("twitter_username"),
                        data.get("twitter_password"),
                    )
                )
                row = await cur.fetchone()
                return self._row_to_tw_profile(row, cur.description)
        finally:
            conn.close()
    
    def _row_to_tw_profile(self, row, description) -> Dict:
        """Преобразует строку БД в словарь профиля Twitter."""
        columns = [col.name for col in description]
        profile = dict(zip(columns, row))
        if isinstance(profile.get("time_intervals"), str):
            profile["time_intervals"] = json.loads(profile["time_intervals"])
        return profile
    
    # ==================== WordPress ====================
    
    async def get_wp_profile(self, user_id: int) -> Optional[Dict]:
        """Получает профиль WordPress пользователя."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM wp_profiles WHERE user_id = %s",
                    (user_id,)
                )
                row = await cur.fetchone()
                if row:
                    return self._row_to_wp_profile(row, cur.description)
                return None
        finally:
            conn.close()
    
    async def save_wp_profile(self, user_id: int, data: Dict) -> Dict:
        """Сохраняет или обновляет профиль WordPress."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO wp_profiles (
                        user_id, publish_enabled, collect_enabled, schedule_type,
                        time_intervals, site_url, username, app_password
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        publish_enabled = EXCLUDED.publish_enabled,
                        collect_enabled = EXCLUDED.collect_enabled,
                        schedule_type = EXCLUDED.schedule_type,
                        time_intervals = EXCLUDED.time_intervals,
                        site_url = EXCLUDED.site_url,
                        username = EXCLUDED.username,
                        app_password = EXCLUDED.app_password,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING *
                    """,
                    (
                        user_id,
                        data.get("publish_enabled", False),
                        data.get("collect_enabled", False),
                        data.get("schedule_type", "immediate"),
                        json.dumps(data.get("time_intervals", [])),
                        data.get("site_url"),
                        data.get("username"),
                        data.get("app_password"),
                    )
                )
                row = await cur.fetchone()
                return self._row_to_wp_profile(row, cur.description)
        finally:
            conn.close()
    
    def _row_to_wp_profile(self, row, description) -> Dict:
        """Преобразует строку БД в словарь профиля WordPress."""
        columns = [col.name for col in description]
        profile = dict(zip(columns, row))
        if isinstance(profile.get("time_intervals"), str):
            profile["time_intervals"] = json.loads(profile["time_intervals"])
        return profile
    
    # ==================== VKontakte ====================
    
    async def get_vk_profile(self, user_id: int) -> Optional[Dict]:
        """Получает профиль VKontakte пользователя."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM vk_profiles WHERE user_id = %s",
                    (user_id,)
                )
                row = await cur.fetchone()
                if row:
                    return self._row_to_vk_profile(row, cur.description)
                return None
        finally:
            conn.close()
    
    async def save_vk_profile(self, user_id: int, data: Dict) -> Dict:
        """Сохраняет или обновляет профиль VKontakte."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO vk_profiles (
                        user_id, publish_enabled, collect_enabled, schedule_type,
                        time_intervals, owner_id, friends_only, from_group,
                        message, attachments, signed, mark_as_ads
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        publish_enabled = EXCLUDED.publish_enabled,
                        collect_enabled = EXCLUDED.collect_enabled,
                        schedule_type = EXCLUDED.schedule_type,
                        time_intervals = EXCLUDED.time_intervals,
                        owner_id = EXCLUDED.owner_id,
                        friends_only = EXCLUDED.friends_only,
                        from_group = EXCLUDED.from_group,
                        message = EXCLUDED.message,
                        attachments = EXCLUDED.attachments,
                        signed = EXCLUDED.signed,
                        mark_as_ads = EXCLUDED.mark_as_ads,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING *
                    """,
                    (
                        user_id,
                        data.get("publish_enabled", False),
                        data.get("collect_enabled", False),
                        data.get("schedule_type", "immediate"),
                        json.dumps(data.get("time_intervals", [])),
                        data.get("owner_id"),
                        data.get("friends_only", False),
                        data.get("from_group", False),
                        data.get("message"),
                        data.get("attachments"),
                        data.get("signed", False),
                        data.get("mark_as_ads", False),
                    )
                )
                row = await cur.fetchone()
                return self._row_to_vk_profile(row, cur.description)
        finally:
            conn.close()
    
    def _row_to_vk_profile(self, row, description) -> Dict:
        """Преобразует строку БД в словарь профиля VKontakte."""
        columns = [col.name for col in description]
        profile = dict(zip(columns, row))
        if isinstance(profile.get("time_intervals"), str):
            profile["time_intervals"] = json.loads(profile["time_intervals"])
        return profile
    
    # ==================== cURL ====================
    
    async def get_curl_settings(self, user_id: int) -> Optional[Dict]:
        """Получает настройки cURL пользователя."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM curl_settings WHERE user_id = %s",
                    (user_id,)
                )
                row = await cur.fetchone()
                if row:
                    return self._row_to_curl_settings(row, cur.description)
                return None
        finally:
            conn.close()
    
    async def save_curl_settings(self, user_id: int, data: Dict) -> Dict:
        """Сохраняет или обновляет настройки cURL."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO curl_settings (
                        user_id, collect_enabled, schedule_type, time_intervals,
                        url, xpath, take_screenshot, to_tg, to_tw, to_vk, to_wp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        collect_enabled = EXCLUDED.collect_enabled,
                        schedule_type = EXCLUDED.schedule_type,
                        time_intervals = EXCLUDED.time_intervals,
                        url = EXCLUDED.url,
                        xpath = EXCLUDED.xpath,
                        take_screenshot = EXCLUDED.take_screenshot,
                        to_tg = EXCLUDED.to_tg,
                        to_tw = EXCLUDED.to_tw,
                        to_vk = EXCLUDED.to_vk,
                        to_wp = EXCLUDED.to_wp,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING *
                    """,
                    (
                        user_id,
                        data.get("collect_enabled", False),
                        data.get("schedule_type", "standard"),
                        json.dumps(data.get("time_intervals", [])),
                        data.get("url"),
                        data.get("xpath"),
                        data.get("take_screenshot", False),
                        data.get("to_tg", False),
                        data.get("to_tw", False),
                        data.get("to_vk", False),
                        data.get("to_wp", False),
                    )
                )
                row = await cur.fetchone()
                return self._row_to_curl_settings(row, cur.description)
        finally:
            conn.close()
    
    def _row_to_curl_settings(self, row, description) -> Dict:
        """Преобразует строку БД в словарь настроек cURL."""
        columns = [col.name for col in description]
        settings = dict(zip(columns, row))
        if isinstance(settings.get("time_intervals"), str):
            settings["time_intervals"] = json.loads(settings["time_intervals"])
        return settings
    
    # ==================== cPost ====================
    
    async def get_cpost_profile(self, user_id: int) -> Optional[Dict]:
        """Получает профиль ручных постов пользователя."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM cpost_profiles WHERE user_id = %s",
                    (user_id,)
                )
                row = await cur.fetchone()
                if row:
                    return self._row_to_cpost_profile(row, cur.description)
                return None
        finally:
            conn.close()
    
    async def save_cpost_profile(self, user_id: int, data: Dict) -> Dict:
        """Сохраняет или обновляет профиль ручных постов."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO cpost_profiles (user_id, default_platforms)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        default_platforms = EXCLUDED.default_platforms,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING *
                    """,
                    (
                        user_id,
                        json.dumps(data.get("default_platforms", {"tg": False, "tw": False, "wp": False, "vk": False})),
                    )
                )
                row = await cur.fetchone()
                return self._row_to_cpost_profile(row, cur.description)
        finally:
            conn.close()
    
    def _row_to_cpost_profile(self, row, description) -> Dict:
        """Преобразует строку БД в словарь профиля ручных постов."""
        columns = [col.name for col in description]
        profile = dict(zip(columns, row))
        if isinstance(profile.get("default_platforms"), str):
            profile["default_platforms"] = json.loads(profile["default_platforms"])
        return profile
    
    # ==================== Методы получения всех профилей ====================
    
    async def get_all_tg_profiles(self) -> list[Dict]:
        """Получает все профили Telegram."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM tg_profiles")
                rows = await cur.fetchall()
                return [self._row_to_tg_profile(row, cur.description) for row in rows]
        finally:
            conn.close()
    
    async def get_all_tw_profiles(self) -> list[Dict]:
        """Получает все профили Twitter."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM tw_profiles")
                rows = await cur.fetchall()
                return [self._row_to_tw_profile(row, cur.description) for row in rows]
        finally:
            conn.close()
    
    async def get_all_wp_profiles(self) -> list[Dict]:
        """Получает все профили WordPress."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM wp_profiles")
                rows = await cur.fetchall()
                return [self._row_to_wp_profile(row, cur.description) for row in rows]
        finally:
            conn.close()
    
    async def get_all_vk_profiles(self) -> list[Dict]:
        """Получает все профили VKontakte."""
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM vk_profiles")
                rows = await cur.fetchall()
                return [self._row_to_vk_profile(row, cur.description) for row in rows]
        finally:
            conn.close()


profile_service = ProfileService()
