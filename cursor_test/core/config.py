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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
