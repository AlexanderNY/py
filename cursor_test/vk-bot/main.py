"""Точка входа VK Bot: FastAPI и фоновые циклы сбора/публикации."""

import asyncio
import logging
import signal
import sys

import uvicorn
from fastapi import FastAPI

from config import settings
from database import init_db, close_db
from services.vk_bot_service import VkBotService


logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="VK Bot Service", version="1.0.0")

bot_service: VkBotService | None = None
_reload_task = None


@app.get("/health")
async def health_check():
    from datetime import datetime
    return {
        "status": "ok",
        "service": "vk-bot",
        "server_time": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/vk/reload")
async def reload_collect():
    """Запускает один проход сбора постов в фоне."""
    global bot_service
    if not bot_service:
        return {"status": "error", "message": "Bot service not initialized"}
    asyncio.create_task(bot_service.run_collect_once())
    return {"status": "ok", "message": "Collect started"}


async def run_api_server():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
    server = uvicorn.Server(config)
    await server.serve()


def signal_handler(signum, frame):
    logger.info("Received signal %s, shutting down...", signum)
    if bot_service:
        asyncio.create_task(bot_service.stop())
    sys.exit(0)


async def _reload_loop():
    interval = settings.RELOAD_PROFILES_INTERVAL_SEC
    if interval <= 0:
        return
    while True:
        await asyncio.sleep(interval)
        if bot_service and bot_service.is_running():
            try:
                logger.info("Scheduled collect run...")
                await bot_service.run_collect_once()
            except Exception as e:
                logger.error("Scheduled collect error: %s", e, exc_info=True)


async def main():
    global bot_service, _reload_task
    try:
        logger.info("Initializing VK Bot...")
        await init_db([])
        logger.info("Database initialized")

        bot_service = VkBotService()
        logger.info("Starting API server on port %s...", settings.API_PORT)
        api_task = asyncio.create_task(run_api_server())
        await asyncio.sleep(1)
        await bot_service.start()

        if settings.RELOAD_PROFILES_INTERVAL_SEC > 0:
            _reload_task = asyncio.create_task(_reload_loop())

        logger.info("VK Bot is running. Press Ctrl+C to stop.")
        await asyncio.gather(api_task)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt, shutting down...")
    except Exception as e:
        logger.error("Error in main: %s", e, exc_info=True)
        raise
    finally:
        if _reload_task:
            _reload_task.cancel()
            try:
                await _reload_task
            except asyncio.CancelledError:
                pass
        if bot_service:
            await bot_service.stop()
        await close_db()
        logger.info("VK Bot stopped")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error("Fatal error: %s", e, exc_info=True)
        sys.exit(1)
