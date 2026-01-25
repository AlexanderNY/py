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
        Профиль WordPress или базовый объект по умолчанию
    """
    user_id = get_user_id_from_header(x_user_id)
    profile = await profile_service.get_wp_profile(user_id)
    if profile:
        return profile
    return {
        "publish_enabled": False,
        "collect_enabled": False,
        "schedule_type": "immediate",
        "time_intervals": [],
        "site_url": None,
        "username": None,
        "app_password": None,
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


@router.get("/profiles")
async def get_all_wp_profiles():
    """Получает все профили WordPress.
    
    Returns:
        Список всех профилей WordPress
    """
    profiles = await profile_service.get_all_wp_profiles()
    return {"profiles": profiles}


@router.get("/posts")
async def get_wp_posts(
    x_user_id: Optional[str] = Header(None),
    limit: int = 50,
    offset: int = 0,
):
    """Возвращает список постов WordPress пользователя из таблицы wp_posts.
    
    Args:
        x_user_id: ID пользователя из заголовка
        limit: Максимальное количество записей
        offset: Смещение для постраничной загрузки
    
    Returns:
        Список постов WordPress
    """
    user_id = get_user_id_from_header(x_user_id)
    posts = await post_service.get_wp_posts(user_id=user_id, limit=limit, offset=offset)
    return posts


@router.post("/post")
async def create_wp_post(
    data: WordPressPost,
    x_user_id: Optional[str] = Header(None)
):
    """Создает пост WordPress в таблице wp_posts.
    
    Args:
        data: Данные поста в формате ui-app (реальный WordPress)
        
    Returns:
        Созданный пост
    """
    user_id = get_user_id_from_header(x_user_id)
    
    try:
        post = await post_service.create_wp_post_record(
            user_id=user_id,
            text=data.post.content,
            title=data.post.title,
        )
        return post
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
