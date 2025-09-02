"""add_workout_type_column

Revision ID: 0e19b26b20e3
Revises: 9cfaeaedd9b7
Create Date: 2025-09-01 12:56:21.152358

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0e19b26b20e3"
down_revision: Union[str, None] = "9cfaeaedd9b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонку workout_type в workouts, если её нет
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'workouts' AND column_name = 'workout_type') THEN
                ALTER TABLE workouts ADD COLUMN workout_type VARCHAR(50) DEFAULT 'OTHER';
            END IF;
        END $$;
    """)

    # Добавляем колонку meal_type в meals, если её нет
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'meals' AND column_name = 'meal_type') THEN
                ALTER TABLE meals ADD COLUMN meal_type VARCHAR(50) DEFAULT 'OTHER';
            END IF;
        END $$;
    """)

    # Добавляем колонку food_name в meals, если её нет
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'meals' AND column_name = 'food_name') THEN
                ALTER TABLE meals ADD COLUMN food_name VARCHAR(200);
            END IF;
        END $$;
    """)

    # Добавляем колонку test_type в lab_results, если её нет
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'lab_results' AND column_name = 'test_type') THEN
                ALTER TABLE lab_results ADD COLUMN test_type VARCHAR(100);
            END IF;
        END $$;
    """)

    # Копируем данные из старых колонок в новые, если старые существуют
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'workouts' AND column_name = 'type') THEN
                UPDATE workouts SET workout_type = type;
                ALTER TABLE workouts DROP COLUMN type;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'meals' AND column_name = 'type') THEN
                UPDATE meals SET meal_type = type;
                ALTER TABLE meals DROP COLUMN type;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'meals' AND column_name = 'name') THEN
                UPDATE meals SET food_name = name;
                ALTER TABLE meals DROP COLUMN name;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'lab_results' AND column_name = 'name') THEN
                UPDATE lab_results SET test_type = name;
                ALTER TABLE lab_results DROP COLUMN name;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Добавляем старые колонки обратно
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'workouts' AND column_name = 'type') THEN
                ALTER TABLE workouts ADD COLUMN type VARCHAR(50);
                UPDATE workouts SET type = workout_type;
                ALTER TABLE workouts DROP COLUMN workout_type;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'meals' AND column_name = 'type') THEN
                ALTER TABLE meals ADD COLUMN type VARCHAR(50);
                UPDATE meals SET type = meal_type;
                ALTER TABLE meals DROP COLUMN meal_type;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'meals' AND column_name = 'name') THEN
                ALTER TABLE meals ADD COLUMN name VARCHAR(200);
                UPDATE meals SET name = food_name;
                ALTER TABLE meals DROP COLUMN food_name;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'lab_results' AND column_name = 'name') THEN
                ALTER TABLE lab_results ADD COLUMN name VARCHAR(100);
                UPDATE lab_results SET name = test_type;
                ALTER TABLE lab_results DROP COLUMN test_type;
            END IF;
        END $$;
    """)
