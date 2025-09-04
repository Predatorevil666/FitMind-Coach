from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.utils import get_utc_now
from api.models.base import Base

if TYPE_CHECKING:
    from api.models.user import User


class WorkoutType(str, Enum):
    """Типы тренировок."""

    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    HIIT = "hiit"
    OTHER = "other"


class Workout(Base):
    """Модель тренировки."""

    __tablename__ = "workouts"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now
    )
    workout_type: Mapped[WorkoutType] = mapped_column(
        default=WorkoutType.OTHER
    )
    name: Mapped[str] = mapped_column(String(100))
    duration_minutes: Mapped[int] = mapped_column()
    intensity: Mapped[Optional[int]] = mapped_column()  # 1-10 scale
    calories_burned: Mapped[Optional[int]] = mapped_column()
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Отношения
    user: Mapped["User"] = relationship(back_populates="workouts")
