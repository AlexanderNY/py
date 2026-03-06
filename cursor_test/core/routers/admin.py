"""Роутер админ-эндпоинтов: статус сервисов и обзор таблиц постов."""

from typing import Optional
from fastapi import APIRouter, Query, Request

from services.admin_service import admin_service
from services.post_service import post_service
from schemas import (
    ServicesStatusResponse,
    PostsTablesResponse,
    PostsListResponse,
    PostRow,
    ProcessorRunResponse,
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
