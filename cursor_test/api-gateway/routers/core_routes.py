from fastapi import APIRouter, Request, Depends
from fastapi.responses import Response

from config import settings
from services.proxy_service import get_proxy_service
from middleware.jwt_validator import get_current_user


router = APIRouter(prefix="/core", tags=["Core"])


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


@router.get("/statistics")
async def get_statistics(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Получает статистику из core сервиса.
    
    GET /core/statistics -> GET /statistics на core сервисе
    Требует JWT аутентификации.
    """
    return await forward_to_core("/statistics", request)


@router.get("/healthcheck")
async def get_healthcheck(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Получает healthcheck из core сервиса.
    
    GET /core/healthcheck -> GET /healthchecks на core сервисе
    Требует JWT аутентификации.
    Внимание: путь меняется с healthcheck на healthchecks!
    """
    return await forward_to_core("/healthchecks", request)


@router.get("/healthchecks")
async def get_healthchecks(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Получает healthcheck из core сервиса.
    
    GET /core/healthchecks -> GET /healthchecks на core сервисе
    Требует JWT аутентификации.
    """
    return await forward_to_core("/healthchecks", request)
