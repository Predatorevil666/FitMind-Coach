"""fix meals columns

Revision ID: fix_meals_columns
Revises: 0e19b26b20e3
Create Date: 2025-09-01 21:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_meals_columns'
down_revision: Union[str, None] = '0e19b26b20e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix meals table columns"""
    
    # Добавляем новые колонки если их нет
    op.execute("""
        DO $$ 
        BEGIN
            -- Добавляем meal_type если не существует
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'meals' AND column_name = 'meal_type') THEN
                ALTER TABLE meals ADD COLUMN meal_type mealtype;
            END IF;
            
            -- Добавляем food_name если не существует
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'meals' AND column_name = 'food_name') THEN
                ALTER TABLE meals ADD COLUMN food_name VARCHAR(100);
            END IF;
            
            -- Добавляем quantity если не существует
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'meals' AND column_name = 'quantity') THEN
                ALTER TABLE meals ADD COLUMN quantity FLOAT;
            END IF;
            
            -- Добавляем unit если не существует
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'meals' AND column_name = 'unit') THEN
                ALTER TABLE meals ADD COLUMN unit VARCHAR(50);
            END IF;
        END $$;
    """)
    
    # Копируем данные из старых колонок в новые
    op.execute("""
        UPDATE meals 
        SET meal_type = type 
        WHERE meal_type IS NULL AND type IS NOT NULL;
        
        UPDATE meals 
        SET food_name = name 
        WHERE food_name IS NULL AND name IS NOT NULL;
    """)
    
    # Удаляем старые колонки
    op.execute("""
        DO $$ 
        BEGIN
            -- Удаляем type если существует
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'meals' AND column_name = 'type') THEN
                ALTER TABLE meals DROP COLUMN type;
            END IF;
            
            -- Удаляем name если существует
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'meals' AND column_name = 'name') THEN
                ALTER TABLE meals DROP COLUMN name;
            END IF;
            
            -- Удаляем foods если существует
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'meals' AND column_name = 'foods') THEN
                ALTER TABLE meals DROP COLUMN foods;
            END IF;
        END $$;
    """)
    
    # Делаем новые колонки обязательными
    op.execute("""
        DO $$ 
        BEGIN
            -- Устанавливаем NOT NULL для meal_type
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'meals' AND column_name = 'meal_type') THEN
                ALTER TABLE meals ALTER COLUMN meal_type SET NOT NULL;
            END IF;
            
            -- Устанавливаем NOT NULL для food_name
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'meals' AND column_name = 'food_name') THEN
                ALTER TABLE meals ALTER COLUMN food_name SET NOT NULL;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Revert meals table columns"""
    
    # Добавляем обратно старые колонки
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'meals' AND column_name = 'type') THEN
                ALTER TABLE meals ADD COLUMN type mealtype;
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'meals' AND column_name = 'name') THEN
                ALTER TABLE meals ADD COLUMN name VARCHAR(100);
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'meals' AND column_name = 'foods') THEN
                ALTER TABLE meals ADD COLUMN foods JSON;
            END IF;
        END $$;
    """)
    
    # Копируем данные обратно
    op.execute("""
        UPDATE meals 
        SET type = meal_type 
        WHERE type IS NULL AND meal_type IS NOT NULL;
        
        UPDATE meals 
        SET name = food_name 
        WHERE name IS NULL AND food_name IS NOT NULL;
    """)
    
    # Удаляем новые колонки
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'meals' AND column_name = 'meal_type') THEN
                ALTER TABLE meals DROP COLUMN meal_type;
            END IF;
            
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'meals' AND column_name = 'food_name') THEN
                ALTER TABLE meals DROP COLUMN food_name;
            END IF;
            
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'meals' AND column_name = 'quantity') THEN
                ALTER TABLE meals DROP COLUMN quantity;
            END IF;
            
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'meals' AND column_name = 'unit') THEN
                ALTER TABLE meals DROP COLUMN unit;
            END IF;
        END $$;
    """)
    
    # Делаем старые колонки обязательными
    op.execute("""
        ALTER TABLE meals ALTER COLUMN type SET NOT NULL;
        ALTER TABLE meals ALTER COLUMN name SET NOT NULL;
    """) 