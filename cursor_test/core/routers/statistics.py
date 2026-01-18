"""Роутер для получения статистики."""

from fastapi import APIRouter
from services.statistics_service import statistics_service
from schemas import StatisticsResponse


router = APIRouter(tags=["Statistics"])


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """Получает статистику постов по всем платформам.
    
    Returns:
        StatisticsResponse: Статистика по платформам
    """
    services = await statistics_service.get_statistics()
    return {"services": services}
