"""Роутер для WordPress профилей и постов."""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from services.profile_service import profile_service
from services.post_service import post_service
from schemas import WordPressProfileCreate, WordPressPost


router = APIRouter(prefix="/wp", tags=["WordPress"])


def get_user_id_from_header(x_user_id: Optional[str] = Header(None)) -> int:
    """Извлекает user_id из заголовка запроса."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")


@router.get("/profile")
async def get_wp_profile(x_user_id: Optional[str] = Header(None)):
    """Получает профиль WordPress пользователя.
    
    Returns:
        Профиль WordPress или пустой объект
    """
    user_id = get_user_id_from_header(x_user_id)
    profile = await profile_service.get_wp_profile(user_id)
    if profile:
        return profile
    return {
        "publish_enabled": False,
        "collect_enabled": False,
        "schedule_type": "immediate",
        "time_intervals": []
    }


@router.post("/profile")
async def save_wp_profile(
    data: WordPressProfileCreate,
    x_user_id: Optional[str] = Header(None)
):
    """Сохраняет профиль WordPress пользователя.
    
    Args:
        data: Данные профиля
        
    Returns:
        Сохраненный профиль
    """
    user_id = get_user_id_from_header(x_user_id)
    profile = await profile_service.save_wp_profile(user_id, data.model_dump())
    return profile


@router.post("/post")
async def create_wp_post(
    data: WordPressPost,
    x_user_id: Optional[str] = Header(None)
):
    """Создает пост для WordPress (max 150000 символов).
    
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
            platform="wp",
            title=data.title,
            to_tg=data.to_tg,
            to_tw=data.to_tw,
            to_wp=data.to_wp,
            to_vk=data.to_vk
        )
        return post
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
