"""Конфигурация tw-bot (X / Twitter)."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки из переменных окружения."""

    DATABASE_URL: str = "dbname=db_bot user=postgres password=1qaz!QAZ host=host.docker.internal"

    LOG_LEVEL: str = "INFO"
    LOG_BOT_ACTIONS: bool = False

    API_PORT: int = 8011

    TWITTER_CLIENT_ID: str = ""
    TWITTER_CLIENT_SECRET: str = ""

    CORE_SERVICE_URL: str = "http://localhost:8002"
    URL_BOT_SERVICE_URL: str = "http://localhost:8007"

    PUBLISH_INTERVAL_SEC: int = 60
    FEED_COLLECT_INTERVAL_SEC: int = 300

    DEFAULT_TWEET_SCREENSHOT_XPATH: str = "//article[@data-testid='tweet']"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
