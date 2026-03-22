"""Роутер для VKontakte профилей и постов."""

import uuid
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Header, File, UploadFile
from fastapi.responses import FileResponse, Response, RedirectResponse

from services.profile_service import profile_service
from services.post_service import post_service
from schemas import VKontakteProfileCreate, VKontaktePost
from storage_client import get_storage
from pydantic import BaseModel
from config import settings


router = APIRouter(prefix="/vk", tags=["VKontakte"])

UPLOADS_VK_DIR = Path("uploads/vk")
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
S3_KEY_PREFIX = "vk/uploads"


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
        "user_access_token": None,
        "vk_connected": False,
        "vk_user_id": None,
        "groups_to_read": [],
        "users_to_read": [],
        "group_to_post": None,
        "post_to_own_wall": False,
    }


VK_OAUTH_SCOPES = "wall,photos,groups,offline"


@router.get("/oauth/url")
async def get_vk_oauth_url(x_user_id: Optional[str] = Header(None)):
    """Возвращает URL авторизации VK OAuth (state = user_id)."""
    user_id = get_user_id_from_header(x_user_id)
    app_id = (getattr(settings, "VK_APP_ID", None) or "").strip()
    redirect_uri = (getattr(settings, "VK_OAUTH_REDIRECT_URI", None) or "").strip()
    if not app_id or not redirect_uri:
        raise HTTPException(
            status_code=503,
            detail="VK OAuth is not configured (VK_APP_ID, VK_OAUTH_REDIRECT_URI)",
        )
    params = {
        "client_id": app_id,
        "display": "page",
        "redirect_uri": redirect_uri,
        "scope": VK_OAUTH_SCOPES,
        "response_type": "code",
        "v": "5.199",
        "state": str(user_id),
    }
    url = f"https://oauth.vk.com/authorize?{urlencode(params)}"
    return {"url": url}


@router.get("/oauth/callback")
async def vk_oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    """Callback VK OAuth: обмен code на access_token, сохранение user_access_token."""
    frontend_url = (settings.FRONTEND_URL or "").rstrip("/")
    vk_page = f"{frontend_url}/vkontakte"
    if error:
        msg = error_description or error
        return RedirectResponse(url=f"{vk_page}?oauth=error&message={msg}")
    if not code or not state:
        return RedirectResponse(url=f"{vk_page}?oauth=error&message=missing_code_or_state")
    try:
        user_id = int(state)
    except (ValueError, TypeError):
        return RedirectResponse(url=f"{vk_page}?oauth=error&message=invalid_state")
    app_id = (getattr(settings, "VK_APP_ID", None) or "").strip()
    app_secret = (getattr(settings, "VK_APP_SECRET", None) or "").strip()
    redirect_uri = (getattr(settings, "VK_OAUTH_REDIRECT_URI", None) or "").strip()
    if not app_id or not app_secret or not redirect_uri:
        return RedirectResponse(url=f"{vk_page}?oauth=error&message=server_config")
    params = {
        "client_id": app_id,
        "client_secret": app_secret,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    token_url = f"https://oauth.vk.com/access_token?{urlencode(params)}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(token_url, timeout=20.0)
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, ValueError):
            return RedirectResponse(url=f"{vk_page}?oauth=error&message=exchange_failed")
    if data.get("error"):
        err = data.get("error_description") or data.get("error") or "oauth_error"
        return RedirectResponse(url=f"{vk_page}?oauth=error&message={err}")
    access_token = data.get("access_token")
    if not access_token:
        return RedirectResponse(url=f"{vk_page}?oauth=error&message=no_token")
    vk_uid = data.get("user_id")
    vk_user_id = int(vk_uid) if vk_uid is not None else None
    await profile_service.save_vk_oauth_tokens(
        user_id=user_id,
        user_access_token=access_token,
        vk_user_id=vk_user_id,
    )
    return RedirectResponse(url=f"{vk_page}?oauth=success")


@router.get("/oauth/status")
async def vk_oauth_status(x_user_id: Optional[str] = Header(None)):
    """Статус подключения пользовательского OAuth VK (по сохранённому user_access_token)."""
    user_id = get_user_id_from_header(x_user_id)
    profile = await profile_service.get_vk_profile(user_id)
    if not profile:
        return {
            "connected": False,
            "message": "Профиль VK не найден. Сохраните настройки профиля или пройдите OAuth.",
            "vk_user_id": None,
        }
    connected = bool(profile.get("vk_connected"))
    return {
        "connected": connected,
        "message": "Аккаунт VK подключён" if connected else "Пользовательский токен VK не сохранён — нажмите «Подключить VK».",
        "vk_user_id": profile.get("vk_user_id"),
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


@router.post("/upload")
async def upload_vk_image(
    image: UploadFile = File(...),
    x_user_id: Optional[str] = Header(None),
):
    """Загружает изображение в единое хранилище (S3) или локально. Возвращает путь для вложения в пост."""
    get_user_id_from_header(x_user_id)
    if not image.filename:
        raise HTTPException(status_code=400, detail="No file name")
    ext = Path(image.filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Allowed formats: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
        )
    name = f"{uuid.uuid4().hex}{ext}"
    content = await image.read()
    storage = get_storage()
    if storage:
        key = f"{S3_KEY_PREFIX}/{name}"
        await storage.put(key, content)
        return {"url": f"/vk/uploads/{name}"}
    UPLOADS_VK_DIR.mkdir(parents=True, exist_ok=True)
    path = UPLOADS_VK_DIR / name
    path.write_bytes(content)
    return {"url": f"/vk/uploads/{name}"}


def _media_type_for_filename(filename: str) -> str:
    """Возвращает media type по расширению файла."""
    ext = (Path(filename).suffix or "").lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "application/octet-stream")


@router.get("/uploads/{filename}")
async def get_vk_upload(filename: str):
    """Отдаёт загруженный файл: из S3 потоком через Core (для доступа из браузера) или FileResponse с локального диска."""
    if "/" in filename or filename.startswith("."):
        raise HTTPException(status_code=400, detail="Invalid filename")
    storage = get_storage()
    if storage:
        key = f"{S3_KEY_PREFIX}/{filename}"
        content = await storage.get_bytes(key)
        if content is None:
            raise HTTPException(status_code=404, detail="File not found")
        return Response(
            content=content,
            media_type=_media_type_for_filename(filename),
            headers={"Content-Disposition": f'inline; filename="{filename}"'},
        )
    file_path = UPLOADS_VK_DIR / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename, media_type=_media_type_for_filename(filename))


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
        post = await post_service.create_vk_post_record(
            user_id=user_id,
            text=data.text,
            images=data.images or [],
            to_tg=data.to_tg,
            to_tw=data.to_tw,
            to_wp=data.to_wp,
            to_vk=data.to_vk,
        )
        return post
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class VKontaktePostUpdate(BaseModel):
    """Тело запроса для обновления поста VK."""
    text: Optional[str] = None
    images: Optional[list] = None
    attachments: Optional[list] = None
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
            images=data.images,
            attachments=data.attachments,
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
