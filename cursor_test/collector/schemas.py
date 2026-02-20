"""Pydantic-модели для Collector API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Ответ healthcheck."""
    status: str
    service: str


class CycleResult(BaseModel):
    """Результат одного цикла сбора/распределения."""
    status: str
    message: str
    count: int


class LoopStatus(BaseModel):
    """Статус одного фонового цикла."""
    last_run_at: Optional[datetime] = None
    total_processed: int = 0
    last_cycle_count: int = 0


class ServiceStatus(BaseModel):
    """Полный статус сервиса."""
    service: str
    version: str
    collect_interval_sec: int
    distribute_interval_sec: int
    collector: LoopStatus
    distributor: LoopStatus


class PlatformMetric(BaseModel):
    """Метрика по одной платформе."""
    platform: str
    table: str
    collected_count: int
    ready_count: int
    processing_count: int


class MetricsResponse(BaseModel):
    """Ответ с метриками по платформам."""
    platforms: list[PlatformMetric]
    posts_table: dict
