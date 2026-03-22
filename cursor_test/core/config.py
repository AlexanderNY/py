from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Конфигурация Core сервиса из переменных окружения."""
    
      # База данных (тот же формат что и auth)
    DATABASE_URL: str = "dbname=db_bot user=postgres password=1qaz!QAZ host=host.docker.internal"
    
    # API Gateway URL для healthcheck запросов
    API_GATEWAY_URL: str = "http://localhost:8000"
    
    # JWT настройки (должны совпадать с auth сервисом)
    JWT_SECRET_KEY: str = "$2b$12$xyiAcpacCfrFN3wl3ayJT."
    JWT_ALGORITHM: str = "HS256"
    
    # Список сервисов для healthcheck
    HEALTHCHECK_SERVICES: List[str] = [
        "auth",
        "core",
        "api-gateway",
        "tg-bot",
        "vk-bot",
        "wp-bot",
        "url-bot",
        "scheduler"
    ]
    
    # URL сервисов для прямого healthcheck
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    TG_BOT_SERVICE_URL: str = "http://localhost:8004"
    VK_BOT_SERVICE_URL: str = "http://localhost:8005"
    WP_BOT_SERVICE_URL: str = "http://localhost:8006"
    URL_BOT_SERVICE_URL: str = "http://localhost:8007"
    SCHEDULER_SERVICE_URL: str = "http://localhost:8003"
    COLLECTOR_SERVICE_URL: str = "http://localhost:8009"
    PROCESSOR_SERVICE_URL: str = "http://localhost:8010"
    
    # Threads (Meta) OAuth
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    THREADS_OAUTH_REDIRECT_URI: str = ""
    FRONTEND_URL: str = "http://localhost:5173"

    # VK OAuth (user_access_token для wall/photos на стене группы)
    VK_APP_ID: str = ""
    VK_APP_SECRET: str = ""
    VK_OAUTH_REDIRECT_URI: str = ""

    # Базовый URL для ссылок в RSS Дзен (item link)
    RSS_BASE_URL: str = "http://localhost:8002"

    # S3-совместимое хранилище (MinIO по умолчанию на 172.20.10.200). Пустые ACCESS_KEY/SECRET_KEY — хранилище отключено (fallback на локальный диск).
    S3_ENDPOINT_URL: str = "http://172.20.10.200:9000"
    S3_BUCKET: str = "uploads"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
