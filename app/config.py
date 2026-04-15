from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения"""

    # Название проекта
    PROJECT_NAME: str = "Todo API"
    VERSION: str = "1.0.0"

    # База данных — теперь может быть PostgreSQL
    DATABASE_URL: str = "sqlite:///./todos.db"  # По умолчанию SQLite

    # Безопасность
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
