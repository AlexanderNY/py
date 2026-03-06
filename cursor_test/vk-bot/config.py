"""Конфигурация VK Bot сервиса."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация из переменных окружения."""

    DATABASE_URL: str = "dbname=db_bot user=postgres password=1qaz!QAZ host=host.docker.internal"

    UPLOADS_DIR: str = "uploads/vk"

    LOG_LEVEL: str = "DEBUG"
    LOG_BOT_ACTIONS: bool = True

    CORE_SERVICE_URL: str = "http://localhost:8002"

    API_PORT: int = 8005

    VK_COLLECT_INTERVAL_SEC: int = 300

    PUBLISH_INTERVAL_SEC: int = 60

    RELOAD_PROFILES_INTERVAL_SEC: int = 300

    PATH_TO_VK_IMAGE: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
