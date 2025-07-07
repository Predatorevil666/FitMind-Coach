import os

from typing import Any, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    # Базовые настройки
    PROJECT_NAME: str = "FitMind-Coach API"
    API_V1_STR: str = "/api/v1"

    # Настройки базы данных
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./fastapi.db"
    )
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    DB_ECHO: bool = False

    # JWT настройки
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Настройки CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", extra="ignore"
    )

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL


settings = Settings()
