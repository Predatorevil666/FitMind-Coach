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
    
    # Исправление значений goal в таблице profiles
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
    
    # Исправление значений workout_type в таблице workouts
    op.execute("""
        UPDATE workouts 
        SET workout_type = CASE 
            WHEN workout_type = 'STRENGTH' THEN 'strength'
            WHEN workout_type = 'CARDIO' THEN 'cardio'
            WHEN workout_type = 'FLEXIBILITY' THEN 'flexibility'
            WHEN workout_type = 'HIIT' THEN 'hiit'
            WHEN workout_type = 'OTHER' THEN 'other'
            ELSE LOWER(workout_type)
        END
        WHERE workout_type != LOWER(workout_type);
    """)
    
    # Исправление значений meal_type в таблице meals
    op.execute("""
        UPDATE meals 
        SET meal_type = CASE 
            WHEN meal_type = 'BREAKFAST' THEN 'breakfast'
            WHEN meal_type = 'LUNCH' THEN 'lunch'
            WHEN meal_type = 'DINNER' THEN 'dinner'
            WHEN meal_type = 'SNACK' THEN 'snack'
            WHEN meal_type = 'OTHER' THEN 'other'
            ELSE LOWER(meal_type)
        END
        WHERE meal_type != LOWER(meal_type);
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
    
    # Откат значений workout_type в таблице workouts
    op.execute("""
        UPDATE workouts 
        SET workout_type = CASE 
            WHEN workout_type = 'strength' THEN 'STRENGTH'
            WHEN workout_type = 'cardio' THEN 'CARDIO'
            WHEN workout_type = 'flexibility' THEN 'FLEXIBILITY'
            WHEN workout_type = 'hiit' THEN 'HIIT'
            WHEN workout_type = 'other' THEN 'OTHER'
            ELSE UPPER(workout_type)
        END
        WHERE workout_type != UPPER(workout_type);
    """)
    
    # Откат значений meal_type в таблице meals
    op.execute("""
        UPDATE meals 
        SET meal_type = CASE 
            WHEN meal_type = 'breakfast' THEN 'BREAKFAST'
            WHEN meal_type = 'lunch' THEN 'LUNCH'
            WHEN meal_type = 'dinner' THEN 'DINNER'
            WHEN meal_type = 'snack' THEN 'SNACK'
            WHEN meal_type = 'other' THEN 'OTHER'
            ELSE UPPER(meal_type)
        END
        WHERE meal_type != UPPER(meal_type);
    """)
