from fastapi import APIRouter, Request, Depends
from fastapi.responses import Response

from config import settings
from services.proxy_service import get_proxy_service
from middleware.jwt_validator import get_current_user


router = APIRouter(prefix="/test", tags=["Test"])


async def forward_to_selectcb(
    target_path: str,
    request: Request,
    override_method: str | None = None
) -> Response:
    """Перенаправляет запрос на selectcb сервис.
    
    Args:
        target_path: Путь на selectcb сервисе
        request: FastAPI Request объект
        override_method: Переопределить HTTP метод (опционально)
    
    Returns:
        Response от selectcb сервиса
    """
    proxy_service = get_proxy_service()
    target_url = proxy_service.build_target_url(settings.SELECTCB_SERVICE_URL, target_path)
    
    return await proxy_service.forward_request(
        target_url=target_url,
        method=request.method,
        request=request,
        override_method=override_method
    )


@router.get("/search/{order_id}")
async def handle_search(
    order_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Обрабатывает запрос поиска заказа.
    
    GET /test/search/{order_id} -> GET /test/search/{order_id} на selectcb сервисе
    Требует JWT аутентификации.
    """
    return await forward_to_selectcb(f"/test/search/{order_id}", request)


@router.get("/products")
async def handle_get_products(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Обрабатывает запрос получения списка продуктов.
    
    GET /test/products -> GET /test/products на selectcb сервисе
    Требует JWT аутентификации.
    """
    return await forward_to_selectcb("/test/products", request)


@router.post("/submit")
async def handle_submit(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Обрабатывает запрос создания заказа.
    
    POST /test/submit -> POST /test/submit на selectcb сервисе
    Требует JWT аутентификации.
    """
    return await forward_to_selectcb("/test/submit", request)
