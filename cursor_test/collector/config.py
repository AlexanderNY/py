"""Конфигурация Collector сервиса из переменных окружения."""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Collector."""

    # База данных
    DATABASE_URL: str = "dbname=db_bot user=postgres password=1qaz!QAZ host=host.docker.internal"

    # Интервалы выполнения (секунды)
    COLLECT_INTERVAL_SEC: int = 60
    DISTRIBUTE_INTERVAL_SEC: int = 60

    # Размер батча за один цикл
    COLLECT_BATCH_SIZE: int = 100
    DISTRIBUTE_BATCH_SIZE: int = 100

    # Порт для FastAPI сервера
    API_PORT: int = 8009

    # Уровень логирования
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


# Реестр исходных таблиц (платформа -> имя таблицы)
# Для добавления новой платформы достаточно добавить одну запись.
SOURCE_TABLES = [
    {"platform": "tg", "table": "tg_posts"},
    {"platform": "wp", "table": "wp_posts"},
    {"platform": "url", "table": "url_posts"},
    # {"platform": "tw", "table": "tw_posts"},
    # {"platform": "vk", "table": "vk_posts"},
]

# Маппинг флагов to_* -> целевые таблицы
TARGET_TABLES = {
    "to_tg": {"platform": "tg", "table": "tg_posts"},
    "to_wp": {"platform": "wp", "table": "wp_posts"},
    # "to_tw": {"platform": "tw", "table": "tw_posts"},
    # "to_vk": {"platform": "vk", "table": "vk_posts"},
}
