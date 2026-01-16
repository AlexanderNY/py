from fastapi import APIRouter, Request, Depends
from fastapi.responses import Response

from config import settings
from services.proxy_service import get_proxy_service
from middleware.jwt_validator import get_current_user


router = APIRouter(prefix="/curl", tags=["Curl"])


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


@router.get("/settings")
async def get_curl_settings(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Получает настройки curl из core сервиса.
    
    GET /curl/settings -> GET /curl/settings на core сервисе
    Требует JWT аутентификации.
    """
    return await forward_to_core("/curl/settings", request)


@router.post("/settings")
async def save_curl_settings(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Сохраняет настройки curl в core сервисе.
    
    POST /curl/settings -> POST /curl/settings на core сервисе
    Требует JWT аутентификации.
    """
    return await forward_to_core("/curl/settings", request)
