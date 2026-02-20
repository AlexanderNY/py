"""Конфигурация Processor сервиса из переменных окружения."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Processor."""

    # База данных
    DATABASE_URL: str = "dbname=db_bot user=postgres password=1qaz!QAZ host=host.docker.internal"

    # Интервал опроса (секунды)
    PROCESS_INTERVAL_SEC: int = 30

    # Размер батча за один цикл
    PROCESS_BATCH_SIZE: int = 50

    # Порт для FastAPI сервера
    API_PORT: int = 8010

    # Уровень логирования
    LOG_LEVEL: str = "INFO"

    # Лимиты длины текста по платформам
    WORDPRESS_MAX_LENGTH: int = 150000
    TELEGRAM_MAX_LENGTH: int = 4096
    TWITTER_MAX_LENGTH: int = 280
    VKONTAKTE_MAX_LENGTH: int = 15985

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


# Маппинг source_platform -> (таблица профиля, название поля process_enabled, поле process_description)
PROFILE_TABLE_MAP = {
    "tg": {
        "table": "tg_profiles",
        "process_flag": "process_enabled",
        "process_description_field": "processing_description",
    },
    "wp": {
        "table": "wp_publish_profile",
        "process_flag": "process_before_publish",
        "process_description_field": "process_description",
    },
    "curl": {
        "table": "curl_settings",
        "process_flag": "process_before_publish",
        "process_description_field": "process_description",
    },
    "url": {
        "table": "curl_settings",
        "process_flag": "process_before_publish",
        "process_description_field": "process_description",
    },
}

# Общие поля настроек обработки, которые читаем из профиля
PROCESSING_SETTINGS_FIELDS = [
    "remove_emojis",
    "remove_images",
    "clean_html",
    "process_services",
    "status_review_after_process",
    "add_static_html",
    "static_html_content",
]

# Маппинг названий платформ -> ключей в конфиге лимитов
PLATFORM_LIMITS = {
    "wordpress": "WORDPRESS_MAX_LENGTH",
    "telegram": "TELEGRAM_MAX_LENGTH",
    "twitter": "TWITTER_MAX_LENGTH",
    "vkontakte": "VKONTAKTE_MAX_LENGTH",
}

# Маппинг флагов to_* -> имя платформы
PLATFORM_FLAGS = {
    "to_wp": "wordpress",
    "to_tg": "telegram",
    "to_tw": "twitter",
    "to_vk": "vkontakte",
}
