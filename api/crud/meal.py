# # from typing import List - unused

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.base import CRUDBase
from api.models.meal import Meal
from api.schemas.meal import MealIn


class CRUDMeal(CRUDBase[Meal, MealIn, MealIn]):
    """
    CRUD-операции для записей о питании.
    """

    async def get_multi_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Meal]:
        """
        Получение списка записей о питании пользователя.
        """
        result = await db.execute(
            select(Meal)
            .where(Meal.user_id == user_id)
            .order_by(Meal.date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_with_user(
        self, db: AsyncSession, *, obj_in: MealIn, user_id: int
    ) -> Meal:
        """
        Создание записи о питании для пользователя.
        """
        db_obj = Meal(
            user_id=user_id,
            date=obj_in.date,
            type=obj_in.type,
            name=obj_in.name,
            calories=obj_in.calories,
            protein_g=obj_in.protein_g,
            carbs_g=obj_in.carbs_g,
            fat_g=obj_in.fat_g,
            notes=obj_in.notes,
            foods=obj_in.foods,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


meal = CRUDMeal(Meal)
