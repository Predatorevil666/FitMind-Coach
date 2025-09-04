from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
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

    # Только telegram_id - основной идентификатор
    telegram_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )

    # Автогенерируемые поля из Telegram
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))

    # Системные поля
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Отношения
    profile: Mapped[Optional["Profile"]] = relationship(
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
    age: Mapped[Optional[int]] = mapped_column(Integer)
    weight: Mapped[Optional[int]] = mapped_column(Integer)  # В килограммах
    height: Mapped[Optional[int]] = mapped_column(Integer)  # В сантиметрах
    goal: Mapped[Optional[str]] = mapped_column(
        String(50), default=Goal.OTHER.value
    )
    target_weight: Mapped[Optional[int]] = mapped_column(
        Integer
    )  # В килограммах
    workouts_per_week: Mapped[Optional[int]] = mapped_column(Integer)
    avg_calories: Mapped[Optional[int]] = mapped_column(Integer)

    # Отношения
    user: Mapped["User"] = relationship(back_populates="profile")
