from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Integer, MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

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


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей."""

    metadata = metadata
    type_annotation_map = {
        dict[str, Any]: dict[str, Any],
    }

    # Конфигурация для использования нативных dataclass-ов
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=get_utc_now)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        default=None, onupdate=get_utc_now
    )
