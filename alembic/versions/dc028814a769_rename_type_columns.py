"""rename_type_columns

Revision ID: dc028814a769
Revises: 2118bbfa414c
Create Date: 2025-09-01 12:36:09.001739

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dc028814a769"
down_revision: Union[str, None] = "2118bbfa414c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Переименовываем колонку type в workout_type в таблице workouts
    op.alter_column("workouts", "type", new_column_name="workout_type")

    # Переименовываем колонку type в meal_type в таблице meals
    op.alter_column("meals", "type", new_column_name="meal_type")

    # Переименовываем колонку name в food_name в таблице meals
    op.alter_column("meals", "name", new_column_name="food_name")

    # Переименовываем колонку name в test_type в таблице lab_results
    op.alter_column("lab_results", "name", new_column_name="test_type")


def downgrade() -> None:
    # Откатываем изменения в обратном порядке
    op.alter_column("lab_results", "test_type", new_column_name="name")
    op.alter_column("meals", "food_name", new_column_name="name")
    op.alter_column("meals", "meal_type", new_column_name="type")
    op.alter_column("workouts", "workout_type", new_column_name="type")
