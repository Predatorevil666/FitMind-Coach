"""fix workouts columns

Revision ID: fix_workouts_columns
Revises: fix_meals_columns
Create Date: 2025-09-01 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'fix_workouts_columns'
down_revision: Union[str, None] = 'fix_meals_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix workouts table columns"""
    
    # Добавляем новые колонки если их нет
    op.execute("""
        DO $$ 
        BEGIN
            -- Добавляем workout_type если не существует
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'workouts' AND column_name = 'workout_type') THEN
                ALTER TABLE workouts ADD COLUMN workout_type workouttype;
            END IF;
            
            -- Добавляем intensity если не существует
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'workouts' AND column_name = 'intensity') THEN
                ALTER TABLE workouts ADD COLUMN intensity INTEGER;
            END IF;
        END $$;
    """)
    
    # Копируем данные из старых колонок в новые
    op.execute("""
        UPDATE workouts 
        SET workout_type = type 
        WHERE workout_type IS NULL AND type IS NOT NULL;
    """)
    
    # Удаляем старые колонки
    op.execute("""
        DO $$ 
        BEGIN
            -- Удаляем type если существует
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'workouts' AND column_name = 'type') THEN
                ALTER TABLE workouts DROP COLUMN type;
            END IF;
            
            -- Удаляем exercises если существует
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'workouts' AND column_name = 'exercises') THEN
                ALTER TABLE workouts DROP COLUMN exercises;
            END IF;
        END $$;
    """)
    
    # Делаем новые колонки обязательными
    op.execute("""
        DO $$ 
        BEGIN
            -- Устанавливаем NOT NULL для workout_type
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'workouts' AND column_name = 'workout_type') THEN
                ALTER TABLE workouts ALTER COLUMN workout_type SET NOT NULL;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Revert workouts table columns"""
    
    # Добавляем обратно старые колонки
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'workouts' AND column_name = 'type') THEN
                ALTER TABLE workouts ADD COLUMN type workouttype;
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'workouts' AND column_name = 'exercises') THEN
                ALTER TABLE workouts ADD COLUMN exercises JSON;
            END IF;
        END $$;
    """)
    
    # Копируем данные обратно
    op.execute("""
        UPDATE workouts 
        SET type = workout_type 
        WHERE type IS NULL AND workout_type IS NOT NULL;
    """)
    
    # Удаляем новые колонки
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'workouts' AND column_name = 'workout_type') THEN
                ALTER TABLE workouts DROP COLUMN workout_type;
            END IF;
            
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'workouts' AND column_name = 'intensity') THEN
                ALTER TABLE workouts DROP COLUMN intensity;
            END IF;
        END $$;
    """)
    
    # Делаем старые колонки обязательными
    op.execute("""
        ALTER TABLE workouts ALTER COLUMN type SET NOT NULL;
    """) 