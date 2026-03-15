"""Конфигурация Instagram Bot сервиса."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация из переменных окружения."""

    DATABASE_URL: str = "dbname=db_bot user=postgres password=1qaz!QAZ host=host.docker.internal"

    UPLOADS_DIR: str = "uploads/instagram"

    LOG_LEVEL: str = "DEBUG"
    LOG_BOT_ACTIONS: bool = True

    API_PORT: int = 8012

    INSTAGRAM_COLLECT_INTERVAL_SEC: int = 300

    PUBLISH_INTERVAL_SEC: int = 60

    RELOAD_PROFILES_INTERVAL_SEC: int = 300

    SESSION_SAVE_PATH: str = ""

    # S3-совместимое хранилище (единое с core).
    S3_ENDPOINT_URL: str = ""
    S3_BUCKET: str = "uploads"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_USE_SSL: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
