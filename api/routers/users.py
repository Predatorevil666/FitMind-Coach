# # from typing import List - unused

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentSuperUser, CurrentUser, SessionDep
from api.crud import profile, user
from api.schemas.user import ProfileIn, ProfileOut, UserIn, UserOut

router = APIRouter(tags=["users"])


@router.post("", response_model=UserOut)
async def create_user(db: SessionDep, user_in: UserIn) -> UserOut:
    """
    Создание нового пользователя.
    """
    # Проверяем, существует ли пользователь с таким email
    db_user = await user.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    # Проверяем, существует ли пользователь с таким username
    db_user = await user.get_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует",
        )

    # Создаем пользователя
    return await user.create(db, obj_in=user_in)


@router.get("/me", response_model=UserOut)
async def read_user_me(current_user: CurrentUser) -> UserOut:
    """
    Получение информации о текущем пользователе.
    """
    return current_user


@router.get("", response_model=list[UserOut])
async def read_users(
    db: SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentSuperUser = None,
) -> list[UserOut]:
    """
    Получение списка пользователей (только для суперпользователей).
    """
    return await user.get_multi(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserOut)
async def read_user(
    user_id: int, db: SessionDep, current_user: CurrentSuperUser = None
) -> UserOut:
    """
    Получение информации о пользователе по ID (только для суперпользователей).
    """
    db_user = await user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return db_user


@router.post("/me/profile", response_model=ProfileOut)
async def create_user_profile(
    db: SessionDep, profile_in: ProfileIn, current_user: CurrentUser
) -> ProfileOut:
    """
    Создание профиля для текущего пользователя.
    """
    # Проверяем, существует ли профиль у пользователя
    db_profile = await profile.get_by_user_id(db, user_id=current_user.id)
    if db_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У пользователя уже есть профиль",
        )

    # Создаем профиль
    return await profile.create_with_user(
        db, obj_in=profile_in, user_id=current_user.id
    )


@router.get("/me/profile", response_model=ProfileOut)
async def read_user_profile(
    db: SessionDep, current_user: CurrentUser
) -> ProfileOut:
    """
    Получение профиля текущего пользователя.
    """
    db_profile = await profile.get_by_user_id(db, user_id=current_user.id)
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден",
        )
    return db_profile


@router.put("/me/profile", response_model=ProfileOut)
async def update_user_profile(
    db: SessionDep, profile_in: ProfileIn, current_user: CurrentUser
) -> ProfileOut:
    """
    Обновление профиля текущего пользователя.
    """
    # Получаем профиль пользователя
    db_profile = await profile.get_by_user_id(db, user_id=current_user.id)
    if not db_profile:
        # Если профиля нет, создаем новый
        return await profile.create_with_user(
            db, obj_in=profile_in, user_id=current_user.id
        )

    # Обновляем профиль
    return await profile.update(db, db_obj=db_profile, obj_in=profile_in)
