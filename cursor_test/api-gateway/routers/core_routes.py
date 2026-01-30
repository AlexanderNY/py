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


@router.get("/schedules")
async def get_schedules(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Получает сводку расписаний из core сервиса.
    
    GET /core/schedules -> GET /schedules на core сервисе.
    Требует JWT аутентификации. Используется scheduler.
    """
    return await forward_to_core("/schedules", request)


@router.get("/users-statistics")
async def get_users_statistics(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Получает статистику использования по пользователям из core сервиса.
    
    GET /core/users-statistics -> GET /users-statistics на core сервисе
    Требует JWT аутентификации и роли admin.
    """
    return await forward_to_core("/users-statistics", request)


@router.get("/schedule")
async def get_schedule(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Получает расписание из core сервиса.
    
    GET /core/schedule -> GET /schedule на core сервисе
    Требует JWT аутентификации и роли admin.
    """
    return await forward_to_core("/schedule", request)


async def forward_to_scheduler(target_path: str, request: Request) -> Response:
    """Перенаправляет запрос на scheduler сервис.
    
    Args:
        target_path: Путь на scheduler сервисе
        request: FastAPI Request объект
    
    Returns:
        Response от scheduler сервиса
    """
    proxy_service = get_proxy_service()
    from config import settings
    target_url = proxy_service.build_target_url(settings.SCHEDULER_SERVICE_URL, target_path)
    
    return await proxy_service.forward_request(
        target_url=target_url,
        method=request.method,
        request=request
    )


@router.post("/start-discovery")
async def start_discovery(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Запускает сбор расписаний на scheduler сервисе.
    
    POST /core/start-discovery -> POST /start-discovery на scheduler сервисе
    Требует JWT аутентификации и роли admin.
    """
    return await forward_to_scheduler("/start-discovery", request)


@router.post("/start-bot")
async def start_bot(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Запускает боты на scheduler сервисе.
    
    POST /core/start-bot -> POST /start-bot на scheduler сервисе
    Требует JWT аутентификации и роли admin.
    """
    return await forward_to_scheduler("/start-bot", request)


@router.post("/notifications")
async def create_notification(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Создает уведомление на core сервисе.
    
    POST /core/notifications -> POST /notifications на core сервисе
    Требует JWT аутентификации и роли admin.
    """
    return await forward_to_core("/notifications", request)


@router.get("/notifications")
async def get_notifications(
    request: Request
) -> Response:
    """Получает уведомления из core сервиса.
    
    GET /core/notifications -> GET /notifications на core сервисе
    Не требует аутентификации - доступно всем пользователям.
    """
    return await forward_to_core("/notifications", request)


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Response:
    """Удаляет уведомление на core сервисе.
    
    DELETE /core/notifications/{id} -> DELETE /notifications/{id} на core сервисе
    Требует JWT аутентификации и роли admin.
    """
    return await forward_to_core(f"/notifications/{notification_id}", request)
