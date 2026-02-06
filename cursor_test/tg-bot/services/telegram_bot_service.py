"""Основной сервис Telegram бота."""

import logging
from typing import Dict
from telethon import events
from telethon.client import TelegramClient

from .client_manager import TelegramClientManager
from .message_handler import MessageHandler
from .post_collector import PostCollector
from .image_handler import ImageHandler


logger = logging.getLogger(__name__)


class TelegramBotService:
    """Основной сервис для управления Telegram ботом."""
    
    def __init__(self):
        """Инициализация сервиса."""
        self.client_manager: TelegramClientManager = None
        self.message_handler = MessageHandler()
        self.post_collector = PostCollector()
        self.image_handler = ImageHandler()
        self._running = False
    
    async def start(self) -> None:
        """Запускает бота и регистрирует обработчики событий."""
        if self._running:
            logger.warning("Bot service is already running")
            return
        
        if not self.client_manager:
            logger.error("Client manager not set")
            return
        
        logger.info("Starting Telegram Bot Service...")
        
        # Загружаем и запускаем все клиенты
        await self.client_manager.start_all_clients()
        
        # Регистрируем обработчики для каждого клиента
        clients = self.client_manager.get_all_clients()
        
        for user_id, client in clients.items():
            profile = self.client_manager.get_profile(user_id)
            if not profile:
                continue
            
            # Получаем список чатов для прослушивания
            chats_to_read = profile.get('chats_to_read', [])
            if not chats_to_read:
                logger.warning(f"No chats_to_read for user {user_id}")
                continue
            
            # Преобразуем в формат для telethon
            chats_list = self.message_handler.get_chats_list(chats_to_read)
            
            if not chats_list:
                logger.warning(f"Empty chats_list for user {user_id}")
                continue
            
            # Регистрируем обработчик для этого клиента
            self._register_handler(client, user_id, profile, chats_list)
            logger.info(f"Registered handler for user {user_id} with {len(chats_list)} chats")
        
        self._running = True
        logger.info("Telegram Bot Service started successfully")
    
    def _register_handler(
        self,
        client: TelegramClient,
        user_id: int,
        profile: Dict,
        chats_list: list
    ) -> None:
        """Регистрирует обработчик событий для клиента.
        
        Args:
            client: TelegramClient для регистрации обработчика
            user_id: ID пользователя
            profile: Профиль пользователя
            chats_list: Список чатов для прослушивания
        """
        save_conditions = profile.get('save_conditions', [])
        
        @client.on(events.NewMessage(chats=chats_list))
        async def handle_new_message(event: events.NewMessage.Event):
            """Обработчик новых сообщений."""
            try:
                # Проверяем Save Conditions
                should_save = self.message_handler.should_save_message(
                    event,
                    save_conditions
                )
                
                if not should_save:
                    logger.debug(f"Message {event.message.id} does not match save conditions")
                    return
                
                logger.info(f"Processing message {event.message.id} for user {user_id}")
                
                # Скачиваем изображения если есть
                images = await self.image_handler.download_images(event, user_id)
                
                # Сохраняем пост в БД
                post = await self.post_collector.save_post(
                    user_id=user_id,
                    event=event,
                    images=images,
                    profile=profile
                )
                
                if post:
                    logger.info(f"Successfully saved post {post.get('id')} for user {user_id}")
                else:
                    logger.error(f"Failed to save post for user {user_id}")
            
            except Exception as e:
                logger.error(f"Error handling message for user {user_id}: {e}", exc_info=True)
    
    async def stop(self) -> None:
        """Останавливает бота."""
        if not self._running:
            return
        
        logger.info("Stopping Telegram Bot Service...")
        if self.client_manager:
            await self.client_manager.stop_all_clients()
        self._running = False
        logger.info("Telegram Bot Service stopped")
    
    async def reload(self) -> None:
        """Перезагружает клиенты и обработчики."""
        logger.info("Reloading Telegram Bot Service...")
        await self.stop()
        await self.start()
    
    def is_running(self) -> bool:
        """Проверяет, запущен ли сервис."""
        return self._running
