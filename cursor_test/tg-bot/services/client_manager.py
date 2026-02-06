"""Управление Telegram клиентами для разных пользователей."""

import json
import logging
import os
from typing import Dict, List, Optional
from telethon import TelegramClient
from telethon.errors import (
    PhoneNumberInvalidError,
    FloodWaitError
)
from database import get_db_connection, release_db_connection
from .notification_service import notification_service


logger = logging.getLogger(__name__)


class TelegramClientManager:
    """Управление множественными TelegramClient для разных пользователей."""
    
    def __init__(self):
        """Инициализация менеджера клиентов."""
        self._clients: Dict[int, TelegramClient] = {}
        self._profiles: Dict[int, Dict] = {}
        self._pending_clients: Dict[int, TelegramClient] = {}  # Клиенты ожидающие авторизации
    
    async def load_profiles(self) -> List[Dict]:
        """Загружает все профили из БД где collect_enabled = TRUE.
        
        Returns:
            Список профилей с включенным сбором сообщений
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT * FROM tg_profiles
                    WHERE collect_enabled = TRUE
                      AND api_id IS NOT NULL
                      AND api_hash IS NOT NULL
                    """
                )
                rows = await cur.fetchall()
                
                if not rows:
                    logger.info("No profiles with collect_enabled found")
                    return []
                
                # Преобразуем строки в словари
                columns = [col.name for col in cur.description]
                profiles = []
                for row in rows:
                    profile = dict(zip(columns, row))
                    # Парсим JSONB поля
                    if isinstance(profile.get('chats_to_read'), str):
                        try:
                            profile['chats_to_read'] = json.loads(profile['chats_to_read'])
                        except (json.JSONDecodeError, TypeError):
                            profile['chats_to_read'] = []
                    if isinstance(profile.get('save_conditions'), str):
                        try:
                            profile['save_conditions'] = json.loads(profile['save_conditions'])
                        except (json.JSONDecodeError, TypeError):
                            profile['save_conditions'] = []
                    profiles.append(profile)
                
                logger.info(f"Loaded {len(profiles)} profiles with collect_enabled")
                return profiles
        finally:
            await release_db_connection(conn)
    
    async def _update_auth_state(
        self,
        user_id: int,
        auth_state: str,
        phone_code_hash: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> None:
        """Обновляет состояние авторизации в БД.
        
        Args:
            user_id: ID пользователя
            auth_state: Новое состояние авторизации
            phone_code_hash: Хеш кода (опционально)
            phone_number: Номер телефона (опционально)
        """
        conn = await get_db_connection()
        try:
            async with conn.cursor() as cur:
                updates = ["auth_state = %s", "updated_at = CURRENT_TIMESTAMP"]
                params = [auth_state]
                
                if phone_code_hash is not None:
                    updates.append("auth_phone_code_hash = %s")
                    params.append(phone_code_hash)
                
                if phone_number is not None:
                    updates.append("auth_phone_number = %s")
                    params.append(phone_number)
                
                params.append(user_id)
                
                await cur.execute(
                    f"""
                    UPDATE tg_profiles
                    SET {', '.join(updates)}
                    WHERE user_id = %s
                    """,
                    params
                )
        finally:
            await release_db_connection(conn)
    
    async def _request_authorization_code(
        self,
        client: TelegramClient,
        phone_number: str,
        user_id: int
    ) -> Optional[str]:
        """Запрашивает код авторизации у Telegram.
        
        Args:
            client: TelegramClient для запроса кода
            phone_number: Номер телефона
            user_id: ID пользователя
            
        Returns:
            phone_code_hash или None в случае ошибки
        """
        try:
            result = await client.send_code_request(phone_number)
            phone_code_hash = result.phone_code_hash
            
            # Сохраняем в БД
            await self._update_auth_state(
                user_id,
                auth_state='pending_code',
                phone_code_hash=phone_code_hash,
                phone_number=phone_number
            )
            
            # Отправляем уведомление пользователю
            await notification_service.send_authorization_notification(
                user_id,
                phone_number
            )
            
            logger.info(f"Authorization code requested for user {user_id}")
            return phone_code_hash
        
        except PhoneNumberInvalidError:
            logger.error(f"Invalid phone number for user {user_id}")
            await notification_service.send_error_notification(
                user_id,
                "Неверный номер телефона. Проверьте номер и попробуйте снова."
            )
            await self._update_auth_state(user_id, auth_state='failed')
            return None
        
        except FloodWaitError as e:
            logger.warning(f"FloodWait error for user {user_id}: {e.seconds} seconds")
            await notification_service.send_error_notification(
                user_id,
                f"Слишком много запросов. Попробуйте через {e.seconds} секунд."
            )
            return None
        
        except Exception as e:
            logger.error(f"Error requesting authorization code for user {user_id}: {e}", exc_info=True)
            await notification_service.send_error_notification(
                user_id,
                f"Ошибка при запросе кода: {str(e)}"
            )
            return None
    
    async def create_client(self, profile: Dict) -> Optional[TelegramClient]:
        """Создает TelegramClient для профиля.
        
        Args:
            profile: Словарь с данными профиля из БД
            
        Returns:
            TelegramClient или None в случае ошибки или необходимости авторизации
        """
        user_id = profile['user_id']
        api_id = profile.get('api_id')
        api_hash = profile.get('api_hash')
        auth_state = profile.get('auth_state', 'authorized')
        
        if not api_id or not api_hash:
            logger.warning(f"Profile {user_id} missing api_id or api_hash")
            return None
        
        try:
            # Создаем директорию для сессий если её нет
            os.makedirs('sessions', exist_ok=True)
            
            # Создаем клиент с уникальным именем сессии для каждого пользователя
            session_name = f'sessions/tg_session_{user_id}'
            client = TelegramClient(
                session_name,
                int(api_id),
                api_hash,
                system_version="4.16.30-vxASPA"
            )
            
            # Подключаемся к Telegram
            try:
                await client.connect()
            except Exception as e:
                logger.error(f"Error connecting client for user {user_id}: {e}")
                return None
            
            # Проверяем авторизацию
            try:
                if not await client.is_user_authorized():
                    # Клиент не авторизован
                    if auth_state == 'authorized':
                        # Первая авторизация - запросить код
                        phone_number = (
                            profile.get('auth_phone_number') or
                            profile.get('telegram_username') or
                            ''
                        )
                        
                        if phone_number:
                            # Убираем @ если есть
                            phone_number = phone_number.lstrip('@')
                            phone_code_hash = await self._request_authorization_code(
                                client, phone_number, user_id
                            )
                            if phone_code_hash:
                                # Сохраняем клиент для последующей авторизации
                                self._pending_clients[user_id] = client
                                return None
                        else:
                            logger.warning(f"No phone number for user {user_id}")
                            await self._update_auth_state(user_id, auth_state='failed')
                            await client.disconnect()
                            return None
                    else:
                        # Ожидаем код или пароль
                        self._pending_clients[user_id] = client
                        return None
                
                # Клиент авторизован
                logger.info(f"Created and connected client for user {user_id}")
                return client
            
            except Exception as e:
                logger.error(f"Error checking authorization for user {user_id}: {e}")
                try:
                    await client.disconnect()
                except:
                    pass
                return None
            
        except Exception as e:
            logger.error(f"Error creating client for user {user_id}: {e}", exc_info=True)
            return None
    
    def get_pending_client(self, user_id: int) -> Optional[TelegramClient]:
        """Получает клиент ожидающий авторизации.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            TelegramClient или None
        """
        return self._pending_clients.get(user_id)
    
    def move_client_to_active(self, user_id: int) -> None:
        """Перемещает клиент из pending в active после успешной авторизации.
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self._pending_clients:
            client = self._pending_clients.pop(user_id)
            self._clients[user_id] = client
            logger.info(f"Moved client for user {user_id} to active")
    
    async def start_all_clients(self) -> None:
        """Запускает все клиенты для профилей с collect_enabled."""
        profiles = await self.load_profiles()
        
        for profile in profiles:
            user_id = profile['user_id']
            
            # Пропускаем если клиент уже существует
            if user_id in self._clients:
                logger.info(f"Client for user {user_id} already exists, skipping")
                continue
            
            client = await self.create_client(profile)
            if client:
                self._clients[user_id] = client
                self._profiles[user_id] = profile
                logger.info(f"Started client for user {user_id}")
            else:
                logger.info(f"Client for user {user_id} pending authorization")
                self._profiles[user_id] = profile
    
    async def stop_all_clients(self) -> None:
        """Останавливает все клиенты."""
        for user_id, client in list(self._clients.items()):
            try:
                await client.disconnect()
                logger.info(f"Stopped client for user {user_id}")
            except Exception as e:
                logger.error(f"Error stopping client for user {user_id}: {e}")
        
        for user_id, client in list(self._pending_clients.items()):
            try:
                await client.disconnect()
                logger.info(f"Stopped pending client for user {user_id}")
            except Exception as e:
                logger.error(f"Error stopping pending client for user {user_id}: {e}")
        
        self._clients.clear()
        self._pending_clients.clear()
        self._profiles.clear()
    
    async def reload_clients(self) -> None:
        """Перезагружает клиенты при изменении профилей."""
        logger.info("Reloading clients...")
        await self.stop_all_clients()
        await self.start_all_clients()
    
    def get_client(self, user_id: int) -> Optional[TelegramClient]:
        """Получает клиент для пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            TelegramClient или None
        """
        return self._clients.get(user_id)
    
    def get_profile(self, user_id: int) -> Optional[Dict]:
        """Получает профиль пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Профиль или None
        """
        return self._profiles.get(user_id)
    
    def get_all_clients(self) -> Dict[int, TelegramClient]:
        """Возвращает все активные клиенты.
        
        Returns:
            Словарь {user_id: TelegramClient}
        """
        return self._clients.copy()
