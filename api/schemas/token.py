from pydantic import BaseModel


class Token(BaseModel):
    """Схема для токенов доступа."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Схема для полезной нагрузки токена."""

    sub: str
    exp: int
    is_refresh: bool = False
    is_superuser: bool = False
