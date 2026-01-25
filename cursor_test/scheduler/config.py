"""Конфигурация Scheduler из config.yaml и переменных окружения."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Настройки Scheduler."""

    API_GATEWAY_URL: str = "http://localhost:8000"
    DATABASE_URL: str = "dbname=db_bot user=postgres password=1qaz!QAZ host=host.docker.internal"

    POLL_INTERVAL_SECONDS: int =  60
    NOTIFY_ON_CHANGE_ONLY: bool =  True

    SCHEDULER_LOGIN: Optional[str] = None
    SCHEDULER_PASSWORD: Optional[str] = None
    SCHEDULER_JWT: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
