from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from api.core.utils import get_utc_now
from api.models.workout import WorkoutType


class WorkoutBase(BaseModel):
    """Базовая схема тренировки."""

    date: datetime = Field(default_factory=get_utc_now)
    type: WorkoutType = WorkoutType.OTHER
    name: str = Field(..., min_length=1, max_length=100)
    duration_minutes: int = Field(..., gt=0)
    calories_burned: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    exercises: Optional[dict] = None


class WorkoutIn(WorkoutBase):
    """Схема для создания тренировки."""

    pass


class WorkoutOut(WorkoutBase):
    """Схема для вывода тренировки."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
