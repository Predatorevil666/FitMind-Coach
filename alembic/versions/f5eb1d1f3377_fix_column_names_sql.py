"""fix_column_names_sql

Revision ID: f5eb1d1f3377
Revises: 3598d34ff2b9
Create Date: 2025-09-01 12:45:09.213714

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f5eb1d1f3377"
down_revision: Union[str, None] = "3598d34ff2b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Используем прямые SQL команды для переименования колонок
    op.execute("ALTER TABLE workouts RENAME COLUMN type TO workout_type;")
    op.execute("ALTER TABLE meals RENAME COLUMN type TO meal_type;")
    op.execute("ALTER TABLE meals RENAME COLUMN name TO food_name;")
    op.execute("ALTER TABLE lab_results RENAME COLUMN name TO test_type;")


def downgrade() -> None:
    # Откатываем изменения
    op.execute("ALTER TABLE lab_results RENAME COLUMN test_type TO name;")
    op.execute("ALTER TABLE meals RENAME COLUMN food_name TO name;")
    op.execute("ALTER TABLE meals RENAME COLUMN meal_type TO type;")
    op.execute("ALTER TABLE workouts RENAME COLUMN workout_type TO type;")
