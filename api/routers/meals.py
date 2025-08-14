# # from typing import List - unused

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentUser, SessionDep
from api.crud import meal
from api.schemas.meal import MealIn, MealOut

router = APIRouter(tags=["meals"])


@router.post("", response_model=MealOut)
async def create_meal(
    db: SessionDep, meal_in: MealIn, current_user: CurrentUser
) -> MealOut:
    """
    Создание новой записи о питании для текущего пользователя.
    """
    return await meal.create_with_user(
        db, obj_in=meal_in, user_id=current_user.id
    )


@router.get("", response_model=list[MealOut])
async def read_meals(
    db: SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = None,
) -> list[MealOut]:
    """
    Получение списка записей о питании текущего пользователя.
    """
    return await meal.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/{meal_id}", response_model=MealOut)
async def read_meal(
    meal_id: int, db: SessionDep, current_user: CurrentUser
) -> MealOut:
    """
    Получение информации о записи о питании по ID.
    """
    db_meal = await meal.get(db, id=meal_id)
    if not db_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись о питании не найдена",
        )

    # Проверяем, принадлежит ли запись о питании текущему пользователю
    if db_meal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )

    return db_meal


@router.put("/{meal_id}", response_model=MealOut)
async def update_meal(
    meal_id: int,
    db: SessionDep,
    meal_in: MealIn,
    current_user: CurrentUser,
) -> MealOut:
    """
    Обновление записи о питании по ID.
    """
    db_meal = await meal.get(db, id=meal_id)
    if not db_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись о питании не найдена",
        )

    # Проверяем, принадлежит ли запись о питании текущему пользователю
    if db_meal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )

    return await meal.update(db, db_obj=db_meal, obj_in=meal_in)


@router.delete("/{meal_id}", response_model=MealOut)
async def delete_meal(
    meal_id: int, db: SessionDep, current_user: CurrentUser
) -> MealOut:
    """
    Удаление записи о питании по ID.
    """
    db_meal = await meal.get(db, id=meal_id)
    if not db_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись о питании не найдена",
        )

    # Проверяем, принадлежит ли запись о питании текущему пользователю
    if db_meal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )

    return await meal.remove(db, id=meal_id)
