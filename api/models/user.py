from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base

if TYPE_CHECKING:
    from api.models.lab import LabResult
    from api.models.meal import Meal
    from api.models.workout import Workout


class Goal(str, Enum):
    """Цели пользователя."""

    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    ENDURANCE = "endurance"
    HEALTH = "health"
    OTHER = "other"


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    telegram_id: Mapped[Optional[int]] = mapped_column(
        unique=True, index=True, nullable=True
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    # Отношения
    profile: Mapped["Profile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    workouts: Mapped[list["Workout"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    meals: Mapped[list["Meal"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    lab_results: Mapped[list["LabResult"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Profile(Base):
    """Профиль пользователя с дополнительной информацией."""

    __tablename__ = "profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    age: Mapped[Optional[int]] = mapped_column()
    weight: Mapped[Optional[float]] = mapped_column()
    height: Mapped[Optional[float]] = mapped_column()
    goal: Mapped[Optional[Goal]] = mapped_column(default=Goal.OTHER)
    target_weight: Mapped[Optional[float]] = mapped_column()
    workouts_per_week: Mapped[Optional[float]] = mapped_column()
    avg_calories: Mapped[Optional[int]] = mapped_column()

    # Отношения
    user: Mapped["User"] = relationship(back_populates="profile")
