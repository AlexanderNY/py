"""Роутер для Twitter профилей и постов."""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from services.profile_service import profile_service
from services.post_service import post_service
from schemas import TwitterProfileCreate, TwitterPost


router = APIRouter(prefix="/tw", tags=["Twitter"])


def get_user_id_from_header(x_user_id: Optional[str] = Header(None)) -> int:
    """Извлекает user_id из заголовка запроса."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")


@router.get("/profile")
async def get_tw_profile(x_user_id: Optional[str] = Header(None)):
    """Получает профиль Twitter пользователя.
    
    Returns:
        Профиль Twitter или пустой объект
    """
    user_id = get_user_id_from_header(x_user_id)
    profile = await profile_service.get_tw_profile(user_id)
    if profile:
        return profile
    return {
        "publish_enabled": False,
        "collect_enabled": False,
        "schedule_type": "immediate",
        "time_intervals": [],
        "use_proxy": False,
        "proxy_user": None,
        "proxy_pass": None,
        "proxy_host": None,
        "proxy_port": None,
        "twitter_username": None,
        "twitter_password": None
    }


@router.post("/profile")
async def save_tw_profile(
    data: TwitterProfileCreate,
    x_user_id: Optional[str] = Header(None)
):
    """Сохраняет профиль Twitter пользователя.
    
    Args:
        data: Данные профиля
    
    Returns:
        Сохраненный профиль
    """
    user_id = get_user_id_from_header(x_user_id)
    profile = await profile_service.save_tw_profile(user_id, data.model_dump())
    return profile


@router.get("/profiles")
async def get_all_tw_profiles():
    """Получает все профили Twitter.
    
    Returns:
        Список всех профилей Twitter
    """
    profiles = await profile_service.get_all_tw_profiles()
    return {"profiles": profiles}


@router.post("/post")
async def create_tw_post(
    data: TwitterPost,
    x_user_id: Optional[str] = Header(None)
):
    """Создает пост для Twitter (max 280 символов).
    
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
            platform="tw",
            to_tg=data.to_tg,
            to_tw=data.to_tw,
            to_wp=data.to_wp,
            to_vk=data.to_vk
        )
        return post
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
