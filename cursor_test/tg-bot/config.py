"""Конфигурация Telegram Bot сервиса."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация из переменных окружения."""
    
    # База данных
    DATABASE_URL: str = "dbname=db_bot user=postgres password=1qaz!QAZ host=host.docker.internal"
    
    # Путь для сохранения изображений
    UPLOADS_DIR: str = "uploads/tg"
    
    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    
    # URL core-service для уведомлений
    CORE_SERVICE_URL: str = "http://localhost:8002"
    
    # Порт для FastAPI сервера
    API_PORT: int = 8004
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
