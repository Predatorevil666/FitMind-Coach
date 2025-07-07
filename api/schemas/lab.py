from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from api.core.utils import get_utc_now


class LabResultBase(BaseModel):
    """Базовая схема результатов лабораторных анализов."""

    date: datetime = Field(default_factory=get_utc_now)
    name: str = Field(..., min_length=1, max_length=100)
    lab_name: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    results: dict = Field(...)


class LabResultIn(LabResultBase):
    """Схема для создания записи о результатах анализов."""

    pass


class LabResultOut(LabResultBase):
    """Схема для вывода записи о результатах анализов."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
