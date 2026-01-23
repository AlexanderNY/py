from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация приложения из переменных окружения."""
    
    # Database
    DATABASE_URL: str = 'dbname=db_bot user=postgres password=1qaz!QAZ host=host.docker.internal'
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
