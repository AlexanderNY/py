"""Роутер для ручных постов (cPost)."""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from services.profile_service import profile_service
from services.post_service import post_service
from schemas import CpostProfileCreate, CpostPost


router = APIRouter(prefix="/cpost", tags=["Manual Posts"])


def get_user_id_from_header(x_user_id: Optional[str] = Header(None)) -> int:
    """Извлекает user_id из заголовка запроса."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")


@router.get("/profile")
async def get_cpost_profile(x_user_id: Optional[str] = Header(None)):
    """Получает профиль ручных постов пользователя.
    
    Returns:
        Профиль или пустой объект
    """
    user_id = get_user_id_from_header(x_user_id)
    profile = await profile_service.get_cpost_profile(user_id)
    if profile:
        return profile
    return {
        "default_platforms": {
            "tg": False,
            "tw": False,
            "wp": False,
            "vk": False
        }
    }


@router.post("/profile")
async def save_cpost_profile(
    data: CpostProfileCreate,
    x_user_id: Optional[str] = Header(None)
):
    """Сохраняет профиль ручных постов пользователя.
    
    Args:
        data: Данные профиля
        
    Returns:
        Сохраненный профиль
    """
    user_id = get_user_id_from_header(x_user_id)
    profile = await profile_service.save_cpost_profile(user_id, data.model_dump())
    return profile


@router.post("/post")
async def create_manual_post(
    data: CpostPost,
    x_user_id: Optional[str] = Header(None)
):
    """Создает ручной пост (max 150000 символов).
    
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
            platform="cpost",
            title=data.title,
            to_tg=data.to_tg,
            to_tw=data.to_tw,
            to_wp=data.to_wp,
            to_vk=data.to_vk
        )
        return post
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
