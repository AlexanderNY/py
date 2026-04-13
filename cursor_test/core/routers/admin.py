"""Роутер админ-эндпоинтов: статус сервисов и обзор таблиц постов."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Query, Request

from dependencies import get_admin_user
from services.admin_service import admin_service
from services.post_service import post_service
from storage_client import get_storage
from schemas import (
    ServicesStatusResponse,
    PostsTablesResponse,
    PostsListResponse,
    PostRow,
    ProcessorRunResponse,
    PostingDiagnosticsResponse,
    StorageFileItem,
    StorageFilesResponse,
    RuntimeLocationResponse,
)


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/services-status", response_model=ServicesStatusResponse)
async def get_services_status():
    """Агрегированный статус всех сервисов (healthcheck + collector/processor/scheduler status)."""
    data = await admin_service.get_services_status()
    return data


@router.post("/processor/run", response_model=ProcessorRunResponse)
async def run_processor_cycle():
    """Принудительный запуск одного цикла обработки на processor."""
    data = await admin_service.run_processor_cycle()
    return ProcessorRunResponse(**data)


@router.post("/collect/run", response_model=ProcessorRunResponse)
async def run_collect_cycle():
    """Принудительный запуск одного цикла сбора на collector (tg_posts → posts)."""
    data = await admin_service.run_collect_cycle()
    return ProcessorRunResponse(**data)


@router.post("/distribute/run", response_model=ProcessorRunResponse)
async def run_distribute_cycle():
    """Принудительный запуск одного цикла распределения на collector (posts ready → tg_posts ready)."""
    data = await admin_service.run_distribute_cycle()
    return ProcessorRunResponse(**data)


@router.get("/posts-tables", response_model=PostsTablesResponse)
async def get_posts_tables():
    """Обзор таблиц постов: метрики из collector и processor."""
    data = await admin_service.get_posts_tables_overview()
    return data


@router.get("/posts", response_model=PostsListResponse)
async def get_admin_posts(
    request: Request,
    limit: int = Query(500, ge=1, le=2000),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="Фильтр по статусу (например review)"),
):
    """Список постов из таблицы posts (все столбцы). При наличии X-User-Id возвращаются только посты этого автора."""
    user_id: Optional[int] = None
    x_user_id = request.headers.get("X-User-Id")
    if x_user_id is not None:
        try:
            user_id = int(x_user_id)
        except ValueError:
            pass
    rows = await post_service.get_all_posts(limit=limit, offset=offset, status=status, user_id=user_id)
    posts = [PostRow.model_validate(r) for r in rows]
    return PostsListResponse(posts=posts)


@router.get("/posting-diagnostics", response_model=PostingDiagnosticsResponse)
async def get_posting_diagnostics():
    """Цикл диагностики постинга: сводки tg_posts/posts по статусам и подсказки для администратора."""
    data = await admin_service.run_posting_diagnostics()
    return PostingDiagnosticsResponse(**data)


@router.get("/runtime-location", response_model=RuntimeLocationResponse)
async def get_runtime_location(admin_user: Dict[str, Any] = Depends(get_admin_user)):
    """Публичный IP, гео по IP и локальный часовой пояс процесса core (контейнера). Только admin."""
    del admin_user
    data = await admin_service.get_runtime_location()
    return RuntimeLocationResponse(**data)


@router.get("/storage/files", response_model=StorageFilesResponse)
async def get_storage_files(
    prefix: Optional[str] = Query(None, description="Фильтр по префиксу ключа (например vk/, uploads/)"),
    limit: int = Query(500, ge=1, le=2000, description="Максимум объектов в ответе"),
    continuation_token: Optional[str] = Query(None, description="Токен для следующей страницы"),
    admin_user: Dict[str, Any] = Depends(get_admin_user),
):
    """Список файлов в едином S3-хранилище. Только admin. Если S3 не настроен — enabled=False."""
    del admin_user  # ensure admin role (checked by dependency)
    storage = get_storage()
    if not storage:
        return StorageFilesResponse(enabled=False, objects=[])
    result = await storage.list_objects(
        prefix=prefix or "",
        max_keys=limit,
        continuation_token=continuation_token,
    )
    items = [StorageFileItem(**obj) for obj in result["objects"]]
    return StorageFilesResponse(
        enabled=True,
        objects=items,
        next_continuation_token=result.get("next_continuation_token"),
    )
