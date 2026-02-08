"""Конфигурация url-bot сервиса из переменных окружения."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация url-bot сервиса."""

    # URL core сервиса (для будущего сохранения постов)
    CORE_SERVICE_URL: str = "http://localhost:8002"

    # API Gateway URL
    API_GATEWAY_URL: str = "http://localhost:8000"

    # Таймаут загрузки страницы (секунды)
    PAGE_LOAD_TIMEOUT_SECONDS: int = 30

    # Таймаут ожидания элемента по XPath (секунды)
    ELEMENT_WAIT_TIMEOUT_SECONDS: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
