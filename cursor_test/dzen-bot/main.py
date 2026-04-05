"""Точка входа Dzen Bot: FastAPI и фоновые циклы Selenium."""

import asyncio
import logging
import signal
import sys

import uvicorn
from fastapi import FastAPI

from config import settings
from database import init_db, close_db
from services.dzen_bot_service import DzenBotService

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dzen Bot Service", version="1.0.0")

bot_service: DzenBotService | None = None
_reload_task: asyncio.Task | None = None


@app.get("/health")
async def health_check():
    from datetime import datetime

    return {
        "status": "ok",
        "service": "dzen-bot",
        "server_time": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/dzen-bot/publish-once")
async def publish_once():
    """Один проход публикации ready-постов."""
    global bot_service
    if not bot_service:
        return {"status": "error", "message": "Bot service not initialized"}
    n = await bot_service.run_publish_once()
    return {"status": "ok", "published": n}


@app.post("/dzen-bot/collect-once")
async def collect_once():
    """Один проход сбора ссылок из студии."""
    global bot_service
    if not bot_service:
        return {"status": "error", "message": "Bot service not initialized"}
    n = await bot_service.run_collect_once()
    return {"status": "ok", "collected": n}


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
    sys.exit(0)


async def _reload_loop():
    interval = settings.RELOAD_PROFILES_INTERVAL_SEC
    if interval <= 0:
        return
    while True:
        await asyncio.sleep(interval)
        if bot_service and bot_service.is_running():
            try:
                await bot_service.run_collect_once()
            except Exception as e:
                logger.error("Scheduled collect error: %s", e, exc_info=True)


async def main():
    global bot_service, _reload_task
    try:
        logger.info("Initializing Dzen Bot...")
        await init_db([])
        logger.info("Database initialized")

        bot_service = DzenBotService()
        api_task = asyncio.create_task(run_api_server())
        await asyncio.sleep(0.5)
        await bot_service.start()

        if settings.RELOAD_PROFILES_INTERVAL_SEC > 0:
            _reload_task = asyncio.create_task(_reload_loop())

        logger.info("Dzen Bot is running on port %s.", settings.API_PORT)
        await api_task
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt, shutting down...")
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
        logger.info("Dzen Bot stopped")


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
