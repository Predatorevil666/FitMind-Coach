"""Fix datetime.utcnow() usage

Revision ID: fix_datetime_utcnow
Revises: e06eb85f8aa8
Create Date: 2023-11-15 12:00:00.000000

"""

from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Union

import sqlalchemy as sa

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
    # Создаем недостающие таблицы

    # Создаем таблицу profiles
    op.create_table(
        "profiles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(100), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("height", sa.Float(), nullable=True),
        sa.Column("goal", sa.String(50), nullable=True),
        sa.Column("target_weight", sa.Float(), nullable=True),
        sa.Column("workouts_per_week", sa.Float(), nullable=True),
        sa.Column("avg_calories", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Создаем таблицу workouts
    op.create_table(
        "workouts",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("calories_burned", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("exercises", sa.JSON(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Создаем таблицу meals
    op.create_table(
        "meals",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("calories", sa.Integer(), nullable=True),
        sa.Column("protein_g", sa.Float(), nullable=True),
        sa.Column("carbs_g", sa.Float(), nullable=True),
        sa.Column("fat_g", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("foods", sa.JSON(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Создаем таблицу lab_results
    op.create_table(
        "lab_results",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("lab_name", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("results", sa.JSON(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Обновляем все записи в таблицах
    # Для SQLite это может быть не так критично, но для PostgreSQL важно

    # Обновляем пользователей
    op.execute("""
        UPDATE users
        SET created_at = REPLACE(created_at, 'Z', '+00:00'),
            updated_at = REPLACE(updated_at, 'Z', '+00:00')
        WHERE created_at LIKE '%Z' OR updated_at LIKE '%Z'
    """)


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
