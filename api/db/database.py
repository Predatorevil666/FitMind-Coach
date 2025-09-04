from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api.core.config import settings

# Создаем движок базы данных
if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
    # Для SQLite используем специальные настройки
    engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        connect_args={"check_same_thread": False},
        echo=settings.DB_ECHO,
    )
else:
    # Для других баз данных (принудительно используем asyncpg для PostgreSQL)
    db_url = settings.SQLALCHEMY_DATABASE_URI
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not db_url.startswith("postgresql+asyncpg://"):
        if "postgresql" in db_url and "+asyncpg" not in db_url:
            db_url = db_url.replace("postgresql", "postgresql+asyncpg", 1)

    engine = create_async_engine(
        db_url,
        echo=settings.DB_ECHO,
    )

# Создаем фабрику сессий
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Контекстный менеджер для получения сессии базы данных.

    Yields:
        AsyncSession: Асинхронная сессия базы данных.
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
