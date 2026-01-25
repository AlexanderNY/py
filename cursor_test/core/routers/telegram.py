"""Роутер для Telegram профилей и постов."""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from services.profile_service import profile_service
from services.post_service import post_service
from schemas import TelegramProfileCreate, TelegramPost


router = APIRouter(prefix="/tg", tags=["Telegram"])


def get_user_id_from_header(x_user_id: Optional[str] = Header(None)) -> int:
    """Извлекает user_id из заголовка запроса.
    
    Args:
        x_user_id: ID пользователя из заголовка
        
    Returns:
        int: ID пользователя
        
    Raises:
        HTTPException: Если заголовок отсутствует или невалиден
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")


@router.get("/profile")
async def get_tg_profile(x_user_id: Optional[str] = Header(None)):
    """Получает профиль Telegram пользователя.
    
    Returns:
        Профиль Telegram или пустой объект
    """
    user_id = get_user_id_from_header(x_user_id)
    profile = await profile_service.get_tg_profile(user_id)
    if profile:
        return profile
    return {
        "publish_enabled": False,
        "collect_enabled": False,
        "schedule_type": "immediate",
        "time_intervals": [],
        "api_id": None,
        "api_hash": None,
        "chats_to_read": [],
        "save_conditions": [],
        "channel_to_post": None,
        "process_enabled": False,
        "processing_description": None
    }


@router.post("/profile")
async def save_tg_profile(
    data: TelegramProfileCreate,
    x_user_id: Optional[str] = Header(None)
):
    """Сохраняет профиль Telegram пользователя.
    
    Args:
        data: Данные профиля
    
    Returns:
        Сохраненный профиль
    """
    user_id = get_user_id_from_header(x_user_id)
    profile = await profile_service.save_tg_profile(user_id, data.model_dump())
    return profile


@router.get("/profiles")
async def get_all_tg_profiles():
    """Получает все профили Telegram.
    
    Returns:
        Список всех профилей Telegram
    """
    profiles = await profile_service.get_all_tg_profiles()
    return {"profiles": profiles}


@router.post("/post")
async def create_tg_post(
    data: TelegramPost,
    x_user_id: Optional[str] = Header(None)
):
    """Создает пост для Telegram (max 4096 символов).
    
    Args:
        data: Данные поста
        
    Returns:
        Созданный пост
    """
    user_id = get_user_id_from_header(x_user_id)
    
    try:
        post = await post_service.create_post(
            user_id=user_id,
            text=data.text,
            platform="tg",
            to_tg=data.to_tg,
            to_tw=data.to_tw,
            to_wp=data.to_wp,
            to_vk=data.to_vk
        )
        return post
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
