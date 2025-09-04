from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Integer, MetaData

try:
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

    MODERN_SQLALCHEMY = True
except ImportError:
    from sqlalchemy import Column
    from sqlalchemy.ext.declarative import declarative_base

    MODERN_SQLALCHEMY = False

from api.core.utils import get_utc_now

# Конвенция именования для PostgreSQL
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

if MODERN_SQLALCHEMY:

    class Base(DeclarativeBase):
        """Базовый класс для всех моделей."""

        metadata = metadata
        type_annotation_map = {
            dict[str, Any]: dict[str, Any],
        }

        # Конфигурация для использования нативных dataclass-ов
        __mapper_args__ = {"eager_defaults": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), default=get_utc_now
        )
        updated_at: Mapped[Optional[datetime]] = mapped_column(
            DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now
        )
else:
    # Старая версия SQLAlchemy
    Base = declarative_base(metadata=metadata)

    # Добавляем общие поля как миксин
    Base.id = Column(Integer, primary_key=True, index=True)
    Base.created_at = Column(DateTime(timezone=True), default=get_utc_now)
    Base.updated_at = Column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now
    )
