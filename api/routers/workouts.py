# # from typing import List - unused

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentUser, SessionDep
from api.crud import workout
from api.schemas.workout import WorkoutIn, WorkoutOut

router = APIRouter(tags=["workouts"])


@router.post("", response_model=WorkoutOut)
async def create_workout(
    db: SessionDep, workout_in: WorkoutIn, current_user: CurrentUser
) -> WorkoutOut:
    """
    Создание новой тренировки для текущего пользователя.
    """
    return await workout.create_with_user(
        db, obj_in=workout_in, user_id=current_user.id
    )


@router.get("", response_model=list[WorkoutOut])
async def read_workouts(
    db: SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = None,
) -> list[WorkoutOut]:
    """
    Получение списка тренировок текущего пользователя.
    """
    return await workout.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/{workout_id}", response_model=WorkoutOut)
async def read_workout(
    workout_id: int, db: SessionDep, current_user: CurrentUser
) -> WorkoutOut:
    """
    Получение информации о тренировке по ID.
    """
    db_workout = await workout.get(db, id=workout_id)
    if not db_workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена",
        )

    # Проверяем, принадлежит ли тренировка текущему пользователю
    if db_workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )

    return db_workout


@router.put("/{workout_id}", response_model=WorkoutOut)
async def update_workout(
    workout_id: int,
    db: SessionDep,
    workout_in: WorkoutIn,
    current_user: CurrentUser,
) -> WorkoutOut:
    """
    Обновление тренировки по ID.
    """
    db_workout = await workout.get(db, id=workout_id)
    if not db_workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена",
        )

    # Проверяем, принадлежит ли тренировка текущему пользователю
    if db_workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )

    return await workout.update(db, db_obj=db_workout, obj_in=workout_in)


@router.delete("/{workout_id}", response_model=WorkoutOut)
async def delete_workout(
    workout_id: int, db: SessionDep, current_user: CurrentUser
) -> WorkoutOut:
    """
    Удаление тренировки по ID.
    """
    db_workout = await workout.get(db, id=workout_id)
    if not db_workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена",
        )

    # Проверяем, принадлежит ли тренировка текущему пользователю
    if db_workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )

    return await workout.remove(db, id=workout_id)
