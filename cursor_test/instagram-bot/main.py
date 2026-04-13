"""Точка входа Instagram Bot: FastAPI и фоновые циклы сбора/публикации."""

import asyncio
import logging
import signal
import sys

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

from config import settings
from database import init_db, close_db
from services.instagram_bot_service import InstagramBotService
from services.instagram_client import InstagramClient
from services.instagram_session import (
    set_instagram_verification_code,
    fetch_instagram_profile_for_login_test,
    get_instagram_last_auth_error,
)


logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Instagram Bot Service", version="1.0.0")

bot_service: InstagramBotService | None = None
_reload_task = None


@app.get("/health")
async def health_check():
    from datetime import datetime
    return {
        "status": "ok",
        "service": "instagram-bot",
        "server_time": datetime.utcnow().isoformat() + "Z",
    }


class InstagramVerifyCodeBody(BaseModel):
    """Одноразовый код 2FA для следующей попытки входа instagrapi."""

    user_id: int = Field(..., ge=1)
    code: str = Field(..., min_length=4, max_length=32)


@app.post("/instagram/verify-code")
async def instagram_set_verification_code(body: InstagramVerifyCodeBody):
    """Сохраняет код 2FA в профиле; бот подхватит его при следующем login и очистит после успеха."""
    await set_instagram_verification_code(body.user_id, body.code)
    return {"status": "ok", "message": "Verification code stored for next login"}


@app.post("/instagram/login-test")
async def instagram_login_test(
    x_user_id: str | None = Header(None, alias="X-User-Id"),
    following_limit: int = Query(
        50,
        ge=0,
        le=200,
        description="Сколько аккаунтов из списка подписок вернуть при успешном входе (0 — не запрашивать)",
    ),
):
    """Проверяет вход в Instagram по учётным данным из БД, обновляет сессию при успехе."""
    if not x_user_id or not str(x_user_id).strip():
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id")
    profile = await fetch_instagram_profile_for_login_test(user_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Instagram profile not found. Save username and password in the app first.",
        )
    username = (profile.get("username") or "").strip()
    password = profile.get("password") or ""
    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail="Username and password must be saved in the profile before login test.",
        )
    client = InstagramClient(
        username,
        password,
        user_id=user_id,
        session_dict=profile.get("instagrapi_session"),
        verification_code=profile.get("instagram_verification_code"),
    )
    ok = await client.login()
    if ok:
        ig_uid = await client.get_self_user_id()
        following: list = []
        if following_limit > 0:
            following = await client.get_self_following(min(following_limit, 200))
        return {
            "ok": True,
            "message": "Login successful",
            "instagram_user_id": ig_uid,
            "following": following,
            "following_count": len(following),
        }
    err = await get_instagram_last_auth_error(user_id)
    return {
        "ok": False,
        "message": err or "Login failed",
    }


@app.post("/instagram/reload")
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
    interval = getattr(settings, "RELOAD_PROFILES_INTERVAL_SEC", 300)
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
        logger.info("Initializing Instagram Bot...")
        await init_db([])
        logger.info("Database initialized")

        bot_service = InstagramBotService()
        logger.info("Starting API server on port %s...", settings.API_PORT)
        api_task = asyncio.create_task(run_api_server())
        await asyncio.sleep(1)
        await bot_service.start()

        if getattr(settings, "RELOAD_PROFILES_INTERVAL_SEC", 0) > 0:
            _reload_task = asyncio.create_task(_reload_loop())

        logger.info("Instagram Bot is running. Press Ctrl+C to stop.")
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
        logger.info("Instagram Bot stopped")


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
