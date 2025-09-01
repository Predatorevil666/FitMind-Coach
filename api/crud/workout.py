# # from typing import List - unused

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.base import CRUDBase
from api.models.workout import Workout
from api.schemas.workout import WorkoutIn


class CRUDWorkout(CRUDBase[Workout, WorkoutIn, WorkoutIn]):
    """
    CRUD-операции для тренировок.
    """

    async def get_multi_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Workout]:
        """
        Получение списка тренировок пользователя.
        """
        result = await db.execute(
            select(Workout)
            .where(Workout.user_id == user_id)
            .order_by(Workout.date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_with_user(
        self, db: AsyncSession, *, obj_in: WorkoutIn, user_id: int
    ) -> Workout:
        """
        Создание тренировки для пользователя.
        """
        db_obj = Workout(
            user_id=user_id,
            date=obj_in.date,
            workout_type=obj_in.workout_type,
            name=obj_in.name,
            duration_minutes=obj_in.duration_minutes,
            intensity=obj_in.intensity,
            calories_burned=obj_in.calories_burned,
            notes=obj_in.notes,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


workout = CRUDWorkout(Workout)
