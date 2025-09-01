from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.base import CRUDBase
from api.models.user import User
from api.schemas.user import TelegramUserCreate, UserIn


class CRUDUser(CRUDBase[User, UserIn, UserIn]):
    """
    CRUD-операции для пользователей с дополнительными методами.
    """

    async def get_by_username(
        self, db: AsyncSession, *, username: str
    ) -> Optional[User]:
        """
        Получение пользователя по имени пользователя.
        """
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_telegram_id(
        self, db: AsyncSession, *, telegram_id: int
    ) -> Optional[User]:
        """
        Получение пользователя по Telegram ID.
        """
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create_from_telegram(
        self, db: AsyncSession, *, obj_in: TelegramUserCreate
    ) -> User:
        """
        Создание пользователя из Telegram данных.
        """
        # Генерируем username если не передан
        username = obj_in.username
        if not username:
            if obj_in.first_name:
                username = f"{obj_in.first_name}_{obj_in.telegram_id}"
            else:
                username = f"user_{obj_in.telegram_id}"

        # Убираем недопустимые символы из username
        username = "".join(c for c in username if c.isalnum() or c in "_-")
        username = username[:50]  # Ограничиваем длину

        # Проверяем уникальность username
        counter = 1
        original_username = username
        while await self.get_by_username(db, username=username):
            username = f"{original_username}_{counter}"
            counter += 1

        db_obj = User(
            telegram_id=obj_in.telegram_id,
            username=username,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            is_active=True,
            is_superuser=False,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create(self, db: AsyncSession, *, obj_in: UserIn) -> User:
        """
        Создание пользователя.
        """
        db_obj = User(
            telegram_id=obj_in.telegram_id,
            username=obj_in.username,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


user = CRUDUser(User)
