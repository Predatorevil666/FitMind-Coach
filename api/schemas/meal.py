from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from api.core.utils import get_utc_now
from api.models.meal import MealType


class MealBase(BaseModel):
    """Базовая схема приема пищи."""

    date: datetime = Field(default_factory=get_utc_now)
    meal_type: MealType = MealType.OTHER
    food_name: str = Field(..., min_length=1, max_length=200)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=50)
    calories: Optional[int] = Field(None, ge=0)
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class MealIn(MealBase):
    """Схема для создания записи о приеме пищи."""

    pass


class MealOut(MealBase):
    """Схема для вывода записи о приеме пищи."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
