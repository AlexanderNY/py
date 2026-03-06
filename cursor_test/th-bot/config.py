"""Конфигурация Threads Bot сервиса."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация из переменных окружения."""

    DATABASE_URL: str = "dbname=db_bot user=postgres password=1qaz!QAZ host=host.docker.internal"

    LOG_LEVEL: str = "INFO"

    # Порт FastAPI
    API_PORT: int = 8009

    # Core (для опроса расписания при необходимости)
    CORE_SERVICE_URL: str = "http://localhost:8002"

    # Meta Threads OAuth
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    THREADS_OAUTH_REDIRECT_URI: str = ""
    THREADS_OAUTH_SCOPE: str = "threads_basic,threads_content_publish"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
