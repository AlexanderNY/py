"""Роутер для cURL настроек скрапинга."""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from services.profile_service import profile_service
from schemas import CurlSettingsCreate


router = APIRouter(prefix="/curl", tags=["cURL"])


def get_user_id_from_header(x_user_id: Optional[str] = Header(None)) -> int:
    """Извлекает user_id из заголовка запроса."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")


@router.get("/settings")
async def get_curl_settings(x_user_id: Optional[str] = Header(None)):
    """Получает настройки cURL скрапинга пользователя.
    
    Returns:
        Настройки cURL или пустой объект
    """
    user_id = get_user_id_from_header(x_user_id)
    settings = await profile_service.get_curl_settings(user_id)
    if settings:
        return settings
    return {
        "collect_enabled": False,
        "urls": [],
        "process_before_publish": False,
        "process_description": None,
        "remove_emojis": False,
        "remove_images": False,
        "clean_html": False,
        "process_services": [],
        "status_review_after_process": False,
        "add_static_html": False,
        "static_html_content": None,
    }


@router.post("/settings")
async def save_curl_settings(
    data: CurlSettingsCreate,
    x_user_id: Optional[str] = Header(None)
):
    """Сохраняет настройки cURL скрапинга пользователя.
    
    Args:
        data: Данные настроек
        
    Returns:
        Сохраненные настройки
    """
    user_id = get_user_id_from_header(x_user_id)
    settings = await profile_service.save_curl_settings(user_id, data.model_dump())
    return settings
