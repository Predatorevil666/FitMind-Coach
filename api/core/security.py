from datetime import timedelta
from typing import Any, Union

from jose import jwt  # type: ignore
from passlib.context import CryptContext  # type: ignore

from api.core.config import settings
from api.core.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_MINUTES,
)
from api.core.utils import get_utc_now

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля."""
    return pwd_context.hash(password)


def create_token(
    subject: Union[str, Any],
    expires_delta: timedelta,
    is_refresh: bool = False,
) -> str:
    """Создание JWT-токена."""
    expire = get_utc_now() + expires_delta

    to_encode = {
        "sub": str(subject),
        "exp": int(expire.timestamp()),
        "is_refresh": is_refresh,
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(subject: Union[str, Any]) -> str:
    """Создание токена доступа."""
    return create_token(
        subject,
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: Union[str, Any]) -> str:
    """Создание токена обновления."""
    return create_token(
        subject,
        timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
        is_refresh=True,
    )
