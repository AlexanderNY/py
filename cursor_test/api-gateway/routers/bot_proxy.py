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
