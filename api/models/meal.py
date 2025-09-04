from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
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
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now
    )
    meal_type: Mapped[MealType] = mapped_column(default=MealType.OTHER)
    food_name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[Optional[float]] = mapped_column()
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    calories: Mapped[Optional[int]] = mapped_column()
    protein_g: Mapped[Optional[float]] = mapped_column()
    carbs_g: Mapped[Optional[float]] = mapped_column()
    fat_g: Mapped[Optional[float]] = mapped_column()
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Отношения
    user: Mapped["User"] = relationship(back_populates="meals")
