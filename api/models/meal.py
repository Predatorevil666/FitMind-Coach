from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.utils import get_utc_now
from api.models.base import Base

if TYPE_CHECKING:
    from api.models.user import User


class MealType(str, Enum):
    """Типы приемов пищи."""

    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    OTHER = "other"


class Meal(Base):
    """Модель приема пищи."""

    __tablename__ = "meals"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    date: Mapped[datetime] = mapped_column(default=get_utc_now)
    type: Mapped[MealType] = mapped_column(default=MealType.OTHER)
    name: Mapped[str] = mapped_column(String(100))
    calories: Mapped[Optional[int]] = mapped_column()
    protein_g: Mapped[Optional[float]] = mapped_column()
    carbs_g: Mapped[Optional[float]] = mapped_column()
    fat_g: Mapped[Optional[float]] = mapped_column()
    notes: Mapped[Optional[str]] = mapped_column(Text)
    foods: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Отношения
    user: Mapped["User"] = relationship(back_populates="meals")
