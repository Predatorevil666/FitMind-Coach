from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.base import CRUDBase
from api.models.user import Profile
from api.schemas.user import ProfileIn


class CRUDProfile(CRUDBase[Profile, ProfileIn, ProfileIn]):
    """
    CRUD-операции для профилей пользователей.
    """

    async def get_by_user_id(
        self, db: AsyncSession, *, user_id: int
    ) -> Optional[Profile]:
        """
        Получение профиля по ID пользователя.
        """
        result = await db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_with_user(
        self, db: AsyncSession, *, obj_in: ProfileIn, user_id: int
    ) -> Profile:
        """
        Создание профиля для пользователя.
        """
        db_obj = Profile(
            user_id=user_id,
            full_name=obj_in.full_name,
            age=obj_in.age,
            weight=obj_in.weight,
            height=obj_in.height,
            goal=obj_in.goal,
            target_weight=obj_in.target_weight,
            workouts_per_week=obj_in.workouts_per_week,
            avg_calories=obj_in.avg_calories,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


profile = CRUDProfile(Profile)
