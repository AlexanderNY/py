"""Основной сервис Telegram бота."""

import asyncio
import logging
from typing import Dict
from telethon import events
from telethon.client import TelegramClient

from config import settings
from .client_manager import TelegramClientManager
from .message_handler import MessageHandler
from .post_collector import PostCollector
from .post_publisher import PostPublisher
from .image_handler import ImageHandler


logger = logging.getLogger(__name__)


def _log_action(msg: str, *args, **kwargs) -> None:
    if settings.LOG_BOT_ACTIONS:
        logger.info(msg, *args, **kwargs)
    else:
        logger.debug(msg, *args, **kwargs)


class TelegramBotService:
    """Основной сервис для управления Telegram ботом."""

    def __init__(self):
        """Инициализация сервиса."""
        self.client_manager: TelegramClientManager = None
        self.message_handler = MessageHandler()
        self.post_collector = PostCollector()
        self.post_publisher: PostPublisher = None
        self.image_handler = ImageHandler()
        self._running = False
        self._publisher_task = None
    
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
            if not profile or not profile.get('collect_enabled'):
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
            _log_action("Registered handler for user %s with %d chats", user_id, len(chats_list))

        # Запускаем фоновую задачу публикации постов
        self.post_publisher = PostPublisher(self.client_manager)
        self._publisher_task = asyncio.create_task(self._publisher_loop())

        self._running = True
        logger.info("Telegram Bot Service started successfully")

    async def _publisher_loop(self) -> None:
        """Цикл проверки и публикации постов со статусом ready."""
        interval = settings.PUBLISH_INTERVAL_SEC
        while self._running:
            try:
                await asyncio.sleep(interval)
                if not self._running:
                    break
                published = await self.post_publisher.publish_ready_posts()
                _log_action("Publisher loop: published %d posts", published)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in publisher loop: {e}", exc_info=True)
    
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
        @client.on(events.NewMessage(chats=chats_list))
        async def handle_new_message(event: events.NewMessage.Event):
            """Обработчик новых сообщений. Сохраняет все сообщения в tg_posts."""
            try:
                _log_action("Processing message %s for user %s", event.message.id, user_id)
                
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
                    _log_action("Successfully saved post %s for user %s", post.get('id'), user_id)
                else:
                    logger.error(f"Failed to save post for user {user_id}")
            
            except Exception as e:
                logger.error(f"Error handling message for user {user_id}: {e}", exc_info=True)
    
    async def stop(self) -> None:
        """Останавливает бота."""
        if not self._running:
            return

        logger.info("Stopping Telegram Bot Service...")
        self._running = False

        if self._publisher_task:
            self._publisher_task.cancel()
            try:
                await self._publisher_task
            except asyncio.CancelledError:
                pass
            self._publisher_task = None

        if self.client_manager:
            await self.client_manager.stop_all_clients()
        logger.info("Telegram Bot Service stopped")
    
    async def reload(self) -> None:
        """Перезагружает клиенты и обработчики."""
        logger.info("Reloading Telegram Bot Service...")
        await self.stop()
        await self.start()
    
    def is_running(self) -> bool:
        """Проверяет, запущен ли сервис."""
        return self._running
