from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.core.deps import SessionDep
from api.core.security import create_access_token, create_refresh_token
from api.crud import user
from api.schemas.token import Token
from api.schemas.user import TelegramAuthRequest

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    db: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    Аутентификация пользователя и получение токенов.
    """
    # Аутентифицируем пользователя
    user_obj = await user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверяем, активен ли пользователь
    if not user_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неактивный пользователь",
        )

    # Создаем токены доступа и обновления
    access_token = create_access_token(user_obj.id)
    refresh_token = create_refresh_token(user_obj.id)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/telegram-auth", response_model=Token)
async def telegram_auth(
    db: SessionDep, telegram_data: TelegramAuthRequest
) -> Token:
    """
    Авторизация пользователя по Telegram ID.
    """
    # Ищем пользователя по telegram_id
    user_obj = await user.get_by_telegram_id(
        db, telegram_id=telegram_data.telegram_id
    )
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с данным Telegram ID не найден. "
            "Необходимо сначала привязать аккаунт.",
        )

    # Проверяем, активен ли пользователь
    if not user_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неактивный пользователь",
        )

    # Создаем токены доступа и обновления
    access_token = create_access_token(user_obj.id)
    refresh_token = create_refresh_token(user_obj.id)

    return Token(access_token=access_token, refresh_token=refresh_token)
