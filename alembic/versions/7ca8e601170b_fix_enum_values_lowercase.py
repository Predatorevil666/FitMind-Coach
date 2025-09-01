"""fix_enum_values_lowercase

Revision ID: 7ca8e601170b
Revises: 0e19b26b20e3
Create Date: 2025-09-01 20:05:00.123456

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '7ca8e601170b'
down_revision: Union[str, None] = '0e19b26b20e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Исправление регистра значений enum полей."""
    
    # 1. Добавляем новые enum значения в нижнем регистре
    
    # Добавляем новые значения в workouttype enum
    op.execute("ALTER TYPE workouttype ADD VALUE 'strength'")
    op.execute("ALTER TYPE workouttype ADD VALUE 'cardio'")
    op.execute("ALTER TYPE workouttype ADD VALUE 'flexibility'")
    op.execute("ALTER TYPE workouttype ADD VALUE 'hiit'")
    op.execute("ALTER TYPE workouttype ADD VALUE 'other'")
    
    # Добавляем новые значения в mealtype enum
    op.execute("ALTER TYPE mealtype ADD VALUE 'breakfast'")
    op.execute("ALTER TYPE mealtype ADD VALUE 'lunch'")
    op.execute("ALTER TYPE mealtype ADD VALUE 'dinner'")
    op.execute("ALTER TYPE mealtype ADD VALUE 'snack'")
    op.execute("ALTER TYPE mealtype ADD VALUE 'other'")
    
    # 2. Обновляем данные в таблицах
    
    # Исправление значений goal в таблице profiles (varchar поле)
    op.execute("""
        UPDATE profiles 
        SET goal = CASE 
            WHEN goal = 'WEIGHT_LOSS' THEN 'weight_loss'
            WHEN goal = 'MUSCLE_GAIN' THEN 'muscle_gain'
            WHEN goal = 'ENDURANCE' THEN 'endurance'
            WHEN goal = 'HEALTH' THEN 'health'
            WHEN goal = 'OTHER' THEN 'other'
            ELSE LOWER(goal)
        END
        WHERE goal != LOWER(goal);
    """)
    
    # Исправление значений type в таблице workouts (enum поле)
    op.execute("""
        UPDATE workouts 
        SET type = CASE 
            WHEN type = 'STRENGTH' THEN 'strength'::workouttype
            WHEN type = 'CARDIO' THEN 'cardio'::workouttype
            WHEN type = 'FLEXIBILITY' THEN 'flexibility'::workouttype
            WHEN type = 'HIIT' THEN 'hiit'::workouttype
            WHEN type = 'OTHER' THEN 'other'::workouttype
            ELSE type
        END;
    """)
    
    # Исправление значений type в таблице meals (enum поле)
    op.execute("""
        UPDATE meals 
        SET type = CASE 
            WHEN type = 'BREAKFAST' THEN 'breakfast'::mealtype
            WHEN type = 'LUNCH' THEN 'lunch'::mealtype
            WHEN type = 'DINNER' THEN 'dinner'::mealtype
            WHEN type = 'SNACK' THEN 'snack'::mealtype
            WHEN type = 'OTHER' THEN 'other'::mealtype
            ELSE type
        END;
    """)


def downgrade() -> None:
    """Откат изменений - возврат к верхнему регистру."""
    
    # Откат значений goal в таблице profiles
    op.execute("""
        UPDATE profiles 
        SET goal = CASE 
            WHEN goal = 'weight_loss' THEN 'WEIGHT_LOSS'
            WHEN goal = 'muscle_gain' THEN 'MUSCLE_GAIN'
            WHEN goal = 'endurance' THEN 'ENDURANCE'
            WHEN goal = 'health' THEN 'HEALTH'
            WHEN goal = 'other' THEN 'OTHER'
            ELSE UPPER(goal)
        END
        WHERE goal != UPPER(goal);
    """)
    
    # Откат значений type в таблице workouts
    op.execute("""
        UPDATE workouts 
        SET type = CASE 
            WHEN type = 'strength' THEN 'STRENGTH'::workouttype
            WHEN type = 'cardio' THEN 'CARDIO'::workouttype
            WHEN type = 'flexibility' THEN 'FLEXIBILITY'::workouttype
            WHEN type = 'hiit' THEN 'HIIT'::workouttype
            WHEN type = 'other' THEN 'OTHER'::workouttype
            ELSE type
        END;
    """)
    
    # Откат значений type в таблице meals
    op.execute("""
        UPDATE meals 
        SET type = CASE 
            WHEN type = 'breakfast' THEN 'BREAKFAST'::mealtype
            WHEN type = 'lunch' THEN 'LUNCH'::mealtype
            WHEN type = 'dinner' THEN 'DINNER'::mealtype
            WHEN type = 'snack' THEN 'SNACK'::mealtype
            WHEN type = 'other' THEN 'OTHER'::mealtype
            ELSE type
        END;
    """)
    
    # Примечание: Удаление enum значений в PostgreSQL сложнее
    # и может привести к проблемам, поэтому оставляем их
