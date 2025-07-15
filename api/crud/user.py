from typing import Any, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.security import get_password_hash, verify_password
from api.crud.base import CRUDBase
from api.models.user import User
from api.schemas.user import UserIn


class CRUDUser(CRUDBase[User, UserIn, UserIn]):
    """
    CRUD-операции для пользователей с дополнительными методами.
    """

    async def get_by_email(
        self, db: AsyncSession, *, email: str
    ) -> Optional[User]:
        """
        Получение пользователя по email.
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

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

    async def link_telegram_id(
        self, db: AsyncSession, *, user_id: int, telegram_id: int
    ) -> Optional[User]:
        """
        Привязка Telegram ID к существующему пользователю.
        """
        # Проверяем, не используется ли уже этот telegram_id
        existing_user = await self.get_by_telegram_id(
            db, telegram_id=telegram_id
        )
        if existing_user and existing_user.id != user_id:
            return None

        # Получаем пользователя и обновляем его telegram_id
        user = await self.get(db, id=user_id)
        if user:
            user.telegram_id = telegram_id
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user

    async def create(self, db: AsyncSession, *, obj_in: UserIn) -> User:
        """
        Создание пользователя с хешированием пароля.
        """
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            telegram_id=obj_in.telegram_id,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: Union[UserIn, dict[str, Any]],
    ) -> User:
        """
        Обновление пользователя с хешированием пароля.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """
        Аутентификация пользователя по email или username.
        """
        # Сначала пытаемся найти по email
        user = await self.get_by_email(db, email=email)

        # Если не найден и это не похоже на email, ищем по username
        if not user and "@" not in email:
            user = await self.get_by_username(db, username=email)

        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user = CRUDUser(User)
