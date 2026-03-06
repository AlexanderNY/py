"""Роутер для VKontakte профилей и постов."""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from services.profile_service import profile_service
from services.post_service import post_service
from schemas import VKontakteProfileCreate, VKontaktePost
from pydantic import BaseModel


router = APIRouter(prefix="/vk", tags=["VKontakte"])


def get_user_id_from_header(x_user_id: Optional[str] = Header(None)) -> int:
    """Извлекает user_id из заголовка запроса."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")


@router.get("/profile")
async def get_vk_profile(x_user_id: Optional[str] = Header(None)):
    """Получает профиль VKontakte пользователя.
    
    Returns:
        Профиль VKontakte или пустой объект
    """
    user_id = get_user_id_from_header(x_user_id)
    profile = await profile_service.get_vk_profile(user_id)
    if profile:
        return profile
    return {
        "publish_enabled": False,
        "collect_enabled": False,
        "schedule_type": "immediate",
        "time_intervals": [],
        "owner_id": None,
        "friends_only": False,
        "from_group": False,
        "message": None,
        "attachments": None,
        "signed": False,
        "mark_as_ads": False,
        "access_token": None,
        "groups_to_read": [],
        "group_to_post": None,
    }


@router.post("/profile")
async def save_vk_profile(
    data: VKontakteProfileCreate,
    x_user_id: Optional[str] = Header(None)
):
    """Сохраняет профиль VKontakte пользователя.
    
    Args:
        data: Данные профиля
    
    Returns:
        Сохраненный профиль
    """
    user_id = get_user_id_from_header(x_user_id)
    profile = await profile_service.save_vk_profile(user_id, data.model_dump())
    return profile


@router.get("/profiles")
async def get_all_vk_profiles():
    """Получает все профили VKontakte.
    
    Returns:
        Список всех профилей VKontakte
    """
    profiles = await profile_service.get_all_vk_profiles()
    return {"profiles": profiles}


@router.get("/posts")
async def get_vk_posts(
    x_user_id: Optional[str] = Header(None),
    limit: int = 50,
    offset: int = 0,
):
    """Возвращает список постов VKontakte пользователя из таблицы vk_posts."""
    user_id = get_user_id_from_header(x_user_id)
    posts = await post_service.get_vk_posts(user_id=user_id, limit=limit, offset=offset)
    return posts


@router.post("/post")
async def create_vk_post(
    data: VKontaktePost,
    x_user_id: Optional[str] = Header(None)
):
    """Создает пост для VKontakte (max 15985 символов).
    
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
            platform="vk",
            to_tg=data.to_tg,
            to_tw=data.to_tw,
            to_wp=data.to_wp,
            to_vk=data.to_vk
        )
        return post
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class VKontaktePostUpdate(BaseModel):
    """Тело запроса для обновления поста VK."""
    text: Optional[str] = None
    status: Optional[str] = None


@router.get("/post/{post_id}")
async def get_vk_post(
    post_id: int,
    x_user_id: Optional[str] = Header(None),
):
    """Возвращает один пост VKontakte по id."""
    user_id = get_user_id_from_header(x_user_id)
    post = await post_service.get_vk_post(user_id=user_id, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/post/{post_id}")
async def update_vk_post(
    post_id: int,
    data: VKontaktePostUpdate,
    x_user_id: Optional[str] = Header(None),
):
    """Обновляет пост VKontakte (текст и/или статус)."""
    user_id = get_user_id_from_header(x_user_id)
    try:
        post = await post_service.update_vk_post(
            user_id=user_id,
            post_id=post_id,
            text=data.text,
            status=data.status,
        )
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/post/{post_id}")
async def delete_vk_post(
    post_id: int,
    x_user_id: Optional[str] = Header(None),
):
    """Помечает пост VKontakte как удаленный (status = deleted)."""
    user_id = get_user_id_from_header(x_user_id)
    post = await post_service.delete_vk_post(user_id=user_id, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
