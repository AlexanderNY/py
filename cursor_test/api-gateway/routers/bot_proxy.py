"""Проксирование запросов к ботам (schedule и др.)."""

from typing import Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import Response

from config import settings
from services.proxy_service import get_proxy_service
from middleware.jwt_validator import get_current_user


router = APIRouter(tags=["Bot Proxy"])


async def _forward_to_bot(service_url: str, path: str, request: Request) -> Response:
    proxy = get_proxy_service()
    target = proxy.build_target_url(service_url.rstrip("/"), path)
    return await proxy.forward_request(target, request.method, request)


@router.post("/tg-bot/auth/code")
async def tg_bot_auth_code(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """POST /tg-bot/auth/code -> tg-bot /tg/auth/code. Требует JWT."""
    return await _forward_to_bot(settings.TG_BOT_SERVICE_URL, "/tg/auth/code", request)


@router.post("/tg-bot/auth/password")
async def tg_bot_auth_password(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """POST /tg-bot/auth/password -> tg-bot /tg/auth/password. Требует JWT."""
    return await _forward_to_bot(settings.TG_BOT_SERVICE_URL, "/tg/auth/password", request)


@router.get("/tg-bot/auth/status/{user_id}")
async def tg_bot_auth_status(
    user_id: int,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """GET /tg-bot/auth/status/{user_id} -> tg-bot /tg/auth/status/{user_id}. Требует JWT."""
    return await _forward_to_bot(settings.TG_BOT_SERVICE_URL, f"/tg/auth/status/{user_id}", request)


@router.get("/tg-bot/channels/{user_id}")
async def tg_bot_channels(
    user_id: int,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """GET /tg-bot/channels/{user_id} -> tg-bot /tg/channels/{user_id}. Требует JWT."""
    return await _forward_to_bot(settings.TG_BOT_SERVICE_URL, f"/tg/channels/{user_id}", request)


@router.post("/tg-bot/reload")
async def tg_bot_reload(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """POST /tg-bot/reload -> tg-bot /tg/reload. Требует JWT."""
    return await _forward_to_bot(settings.TG_BOT_SERVICE_URL, "/tg/reload", request)


@router.post("/tg-bot/schedule")
async def tg_bot_schedule(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """POST /tg-bot/schedule -> tg-bot /schedule. Требует JWT."""
    return await _forward_to_bot(settings.TG_BOT_SERVICE_URL, "/schedule", request)


@router.post("/wp-bot/schedule")
async def wp_bot_schedule(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """POST /wp-bot/schedule -> wp-bot /schedule. Требует JWT."""
    return await _forward_to_bot(settings.WP_BOT_SERVICE_URL, "/schedule", request)


@router.post("/vk-bot/schedule")
async def vk_bot_schedule(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """POST /vk-bot/schedule -> vk-bot /schedule. Требует JWT."""
    return await _forward_to_bot(settings.VK_BOT_SERVICE_URL, "/schedule", request)


@router.post("/url-bot/schedule")
async def url_bot_schedule(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """POST /url-bot/schedule -> url-bot /schedule. Требует JWT."""
    return await _forward_to_bot(settings.URL_BOT_SERVICE_URL, "/schedule", request)


@router.post("/url-bot/run")
async def url_bot_run(request: Request) -> Response:
    """POST /url-bot/run -> url-bot /run. Тестовый запуск скрапинга по запросу (без JWT)."""
    return await _forward_to_bot(settings.URL_BOT_SERVICE_URL, "/run", request)


# ==================== Dzen Bot ====================

@router.get("/dzen-bot/health")
async def dzen_bot_health(request: Request) -> Response:
    """GET /dzen-bot/health -> dzen-bot /health (без JWT)."""
    return await _forward_to_bot(settings.DZEN_BOT_SERVICE_URL, "/health", request)


@router.post("/dzen-bot/publish-once")
async def dzen_bot_publish_once(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """POST /dzen-bot/publish-once -> dzen-bot. Требует JWT."""
    return await _forward_to_bot(settings.DZEN_BOT_SERVICE_URL, "/dzen-bot/publish-once", request)


@router.post("/dzen-bot/collect-once")
async def dzen_bot_collect_once(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """POST /dzen-bot/collect-once -> dzen-bot. Требует JWT."""
    return await _forward_to_bot(settings.DZEN_BOT_SERVICE_URL, "/dzen-bot/collect-once", request)


# ==================== Threads Bot ====================

@router.get("/threads-bot/auth/status/{user_id}")
async def threads_bot_auth_status(
    user_id: int,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """GET /th-bot/auth/status/{user_id} -> th-bot."""
    return await _forward_to_bot(
        settings.THREADS_BOT_SERVICE_URL,
        f"/threads/auth/status/{user_id}",
        request,
    )


@router.get("/threads-bot/auth/url")
async def threads_bot_auth_url(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """GET /th-bot/auth/url -> th-bot (OAuth URL для редиректа)."""
    return await _forward_to_bot(
        settings.THREADS_BOT_SERVICE_URL,
        "/threads/auth/url",
        request,
    )


@router.post("/threads-bot/reload")
async def threads_bot_reload(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """POST /th-bot/reload -> th-bot."""
    return await _forward_to_bot(
        settings.THREADS_BOT_SERVICE_URL,
        "/threads/reload",
        request,
    )


@router.post("/threads-bot/schedule")
async def threads_bot_schedule(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Response:
    """POST /th-bot/schedule -> th-bot."""
    return await _forward_to_bot(
        settings.THREADS_BOT_SERVICE_URL,
        "/schedule",
        request,
    )


# ==================== Instagram Bot ====================

@router.post("/instagram-bot/reload")
async def instagram_bot_reload(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """POST /instagram-bot/reload -> instagram-bot /instagram/reload (один проход сбора)."""
    return await _forward_to_bot(settings.INSTAGRAM_BOT_SERVICE_URL, "/instagram/reload", request)


@router.post("/instagram-bot/verify-code")
async def instagram_bot_verify_code(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """POST /instagram-bot/verify-code -> instagram-bot /instagram/verify-code (2FA)."""
    return await _forward_to_bot(settings.INSTAGRAM_BOT_SERVICE_URL, "/instagram/verify-code", request)
