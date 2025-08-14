from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from api.models.user import Goal


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    telegram_id: Optional[int] = None
    is_active: bool = True
    is_superuser: bool = False


class UserIn(UserBase):
    """Схема для создания пользователя."""

    password: str = Field(..., min_length=8)


class UserOut(UserBase):
    """Схема для вывода пользователя."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TelegramAuthRequest(BaseModel):
    """Схема для авторизации по Telegram ID."""

    telegram_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None


class TelegramLinkRequest(BaseModel):
    """Схема для привязки Telegram ID к аккаунту."""

    email: EmailStr
    password: str
    telegram_id: int


class ProfileBase(BaseModel):
    """Базовая схема профиля."""

    full_name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    goal: Optional[Goal] = Goal.OTHER
    target_weight: Optional[float] = None
    workouts_per_week: Optional[float] = None
    avg_calories: Optional[int] = None


class ProfileIn(ProfileBase):
    """Схема для создания/обновления профиля."""

    pass


class ProfileOut(ProfileBase):
    """Схема для вывода профиля."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
