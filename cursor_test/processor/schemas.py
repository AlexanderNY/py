"""Pydantic модели для Processor API."""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class HealthResponse(BaseModel):
    """Ответ healthcheck."""
    status: str
    service: str


class CycleResult(BaseModel):
    """Результат одного цикла обработки."""
    status: str
    message: str
    count: int


class LoopStatus(BaseModel):
    """Статус фонового цикла."""
    last_run_at: Optional[datetime] = None
    total_processed: int = 0
    last_cycle_count: int = 0


class ServiceStatus(BaseModel):
    """Полный статус сервиса."""
    service: str
    version: str
    process_interval_sec: int
    processor: LoopStatus


class MetricsResponse(BaseModel):
    """Метрики обработки постов."""
    posts_table: Dict[str, Any]
