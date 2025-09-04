"""safe_rename_columns

Revision ID: 9cfaeaedd9b7
Revises: f5eb1d1f3377
Create Date: 2025-09-01 12:52:56.831287

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9cfaeaedd9b7"
down_revision: Union[str, None] = "f5eb1d1f3377"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Безопасное переименование колонок с проверкой существования

    # Переименовываем type в workout_type в таблице workouts, если колонка type существует
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'workouts' AND column_name = 'type') THEN
                ALTER TABLE workouts RENAME COLUMN type TO workout_type;
            END IF;
        END $$;
    """)

    # Переименовываем type в meal_type в таблице meals, если колонка type существует
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'meals' AND column_name = 'type') THEN
                ALTER TABLE meals RENAME COLUMN type TO meal_type;
            END IF;
        END $$;
    """)

    # Переименовываем name в food_name в таблице meals, если колонка name существует
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'meals' AND column_name = 'name') THEN
                ALTER TABLE meals RENAME COLUMN name TO food_name;
            END IF;
        END $$;
    """)

    # Переименовываем name в test_type в таблице lab_results, если колонка name существует
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'lab_results' AND column_name = 'name') THEN
                ALTER TABLE lab_results RENAME COLUMN name TO test_type;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Откатываем изменения
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'lab_results' AND column_name = 'test_type') THEN
                ALTER TABLE lab_results RENAME COLUMN test_type TO name;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'meals' AND column_name = 'food_name') THEN
                ALTER TABLE meals RENAME COLUMN food_name TO name;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'meals' AND column_name = 'meal_type') THEN
                ALTER TABLE meals RENAME COLUMN meal_type TO type;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'workouts' AND column_name = 'workout_type') THEN
                ALTER TABLE workouts RENAME COLUMN workout_type TO type;
            END IF;
        END $$;
    """)
