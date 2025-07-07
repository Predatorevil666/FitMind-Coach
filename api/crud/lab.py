# # from typing import List - unused

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.base import CRUDBase
from api.models.lab import LabResult
from api.schemas.lab import LabResultIn


class CRUDLabResult(CRUDBase[LabResult, LabResultIn, LabResultIn]):
    """
    CRUD-операции для результатов лабораторных анализов.
    """

    async def get_multi_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LabResult]:
        """
        Получение списка результатов анализов пользователя.
        """
        result = await db.execute(
            select(LabResult)
            .where(LabResult.user_id == user_id)
            .order_by(LabResult.date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_with_user(
        self, db: AsyncSession, *, obj_in: LabResultIn, user_id: int
    ) -> LabResult:
        """
        Создание записи о результатах анализов для пользователя.
        """
        db_obj = LabResult(
            user_id=user_id,
            date=obj_in.date,
            name=obj_in.name,
            lab_name=obj_in.lab_name,
            notes=obj_in.notes,
            results=obj_in.results,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


lab_result = CRUDLabResult(LabResult)
