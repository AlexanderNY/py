"""Роутер админ-эндпоинтов: статус сервисов и обзор таблиц постов."""

from fastapi import APIRouter

from services.admin_service import admin_service
from schemas import ServicesStatusResponse, PostsTablesResponse


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/services-status", response_model=ServicesStatusResponse)
async def get_services_status():
    """Агрегированный статус всех сервисов (healthcheck + collector/processor/scheduler status)."""
    data = await admin_service.get_services_status()
    return data


@router.get("/posts-tables", response_model=PostsTablesResponse)
async def get_posts_tables():
    """Обзор таблиц постов: метрики из collector и processor."""
    data = await admin_service.get_posts_tables_overview()
    return data
