"""Точка входа tw-bot: FastAPI и фоновые циклы."""

import asyncio
import logging
import signal
import sys

import uvicorn
from fastapi import FastAPI

from config import settings
from database import close_db, init_db
from services.tw_bot_service import TwBotService

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Twitter / X Bot Service", version="1.0.0")

bot_service: TwBotService | None = None


@app.get("/health")
async def health_check():
    from datetime import datetime

    return {
        "status": "ok",
        "service": "tw-bot",
        "server_time": datetime.utcnow().isoformat() + "Z",
    }


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


async def main():
    global bot_service
    try:
        logger.info("Initializing tw-bot...")
        await init_db([])
        logger.info("Database pool ready")

        bot_service = TwBotService()
        api_task = asyncio.create_task(run_api_server())
        await asyncio.sleep(0.5)
        await bot_service.start()

        logger.info("tw-bot is running on port %s", settings.API_PORT)
        await api_task
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt, shutting down...")
    except Exception as e:
        logger.error("Error in main: %s", e, exc_info=True)
        raise
    finally:
        if bot_service:
            await bot_service.stop()
        await close_db()
        logger.info("tw-bot stopped")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error("Fatal: %s", e, exc_info=True)
        sys.exit(1)
