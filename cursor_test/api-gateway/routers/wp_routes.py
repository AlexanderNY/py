from fastapi import APIRouter, Request, Depends
from fastapi.responses import Response

from config import settings
from services.proxy_service import get_proxy_service
from middleware.jwt_validator import get_current_user


router = APIRouter(prefix="/wp", tags=["WordPress"])


async def forward_to_core(target_path: str, request: Request) -> Response:
    """Перенаправляет запрос на core сервис.
    
    Args:
        target_path: Путь на core сервисе
        request: FastAPI Request объект
    
    Returns:
        Response от core сервиса
    """
    proxy_service = get_proxy_service()
    target_url = proxy_service.build_target_url(settings.CORE_SERVICE_URL, target_path)
    
    return await proxy_service.forward_request(
        target_url=target_url,
        method=request.method,
        request=request
    )


@router.get("/profile")
async def get_wp_profile(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Получает профиль WordPress из core сервиса.
    
    GET /wp/profile -> GET /wp/profile на core сервисе
    Требует JWT аутентификации.
    """
    return await forward_to_core("/wp/profile", request)


@router.post("/profile")
async def save_wp_profile(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Сохраняет профиль WordPress в core сервисе.
    
    POST /wp/profile -> POST /wp/profile на core сервисе
    Требует JWT аутентификации.
    """
    return await forward_to_core("/wp/profile", request)


@router.get("/profiles")
async def get_all_wp_profiles(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Получает все профили WordPress из core сервиса.
    
    GET /wp/profiles -> GET /wp/profiles на core сервисе
    Требует JWT аутентификации.
    """
    return await forward_to_core("/wp/profiles", request)


@router.get("/posts")
async def list_wp_posts(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Возвращает список постов WordPress из core сервиса.
    
    GET /wp/posts -> GET /wp/posts на core сервисе
    Требует JWT аутентификации.
    """
    return await forward_to_core("/wp/posts", request)


@router.post("/post")
async def create_wp_post(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Создает пост WordPress в core сервисе.
    
    POST /wp/post -> POST /wp/post на core сервисе
    Требует JWT аутентификации.
    """
    return await forward_to_core("/wp/post", request)
