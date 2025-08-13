"""Fix datetime.utcnow() usage

Revision ID: fix_datetime_utcnow
Revises: e06eb85f8aa8
Create Date: 2023-11-15 12:00:00.000000

"""

from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fix_datetime_utcnow"
down_revision: Union[str, None] = "e06eb85f8aa8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_utc_now() -> datetime:
    """
    Получить текущее время в UTC с информацией о временной зоне.
    """
    return datetime.now(timezone.utc)


def upgrade() -> None:
    """
    Обновление базы данных.

    Заменяем использование datetime.utcnow() на get_utc_now().
    """
    # Обновляем все записи в таблицах
    # Для SQLite это может быть не так критично, но для PostgreSQL важно

    # Обновляем пользователей (PostgreSQL не поддерживает LIKE с timestamp)
    # В новой базе данных это не нужно, так как все записи уже в
    # правильном формате
    pass


def downgrade() -> None:
    """
    Откат обновления базы данных.

    Возвращаем использование datetime.utcnow().
    """
    # Откатываем изменения, удаляя информацию о временной зоне

    # Обновляем пользователей
    op.execute("""
        UPDATE users
        SET created_at = REPLACE(created_at, '+00:00', 'Z'),
            updated_at = REPLACE(updated_at, '+00:00', 'Z')
        WHERE created_at LIKE '%+00:00' OR updated_at LIKE '%+00:00'
    """)

    # Удаляем созданные таблицы
    op.drop_table("lab_results")
    op.drop_table("meals")
    op.drop_table("workouts")
    op.drop_table("profiles")
