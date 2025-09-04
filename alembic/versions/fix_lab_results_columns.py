"""fix lab results columns

Revision ID: fix_lab_results_columns
Revises: fix_workouts_columns
Create Date: 2025-09-01 22:35:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'fix_lab_results_columns'
down_revision: Union[str, None] = 'fix_workouts_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix lab_results table columns"""
    
    # Добавляем новые колонки если их нет
    op.execute("""
        DO $$ 
        BEGIN
            -- Добавляем test_type если не существует
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'lab_results' AND column_name = 'test_type') THEN
                ALTER TABLE lab_results ADD COLUMN test_type VARCHAR(100);
            END IF;
        END $$;
    """)
    
    # Копируем данные из старых колонок в новые
    op.execute("""
        UPDATE lab_results 
        SET test_type = name 
        WHERE test_type IS NULL AND name IS NOT NULL;
    """)
    
    # Удаляем старые колонки
    op.execute("""
        DO $$ 
        BEGIN
            -- Удаляем name если существует
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'lab_results' AND column_name = 'name') THEN
                ALTER TABLE lab_results DROP COLUMN name;
            END IF;
            
            -- Удаляем lab_name если существует
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'lab_results' AND column_name = 'lab_name') THEN
                ALTER TABLE lab_results DROP COLUMN lab_name;
            END IF;
        END $$;
    """)
    
    # Делаем новые колонки обязательными
    op.execute("""
        DO $$ 
        BEGIN
            -- Устанавливаем NOT NULL для test_type
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'lab_results' AND column_name = 'test_type') THEN
                ALTER TABLE lab_results ALTER COLUMN test_type SET NOT NULL;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Revert lab_results table columns"""
    
    # Добавляем обратно старые колонки
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'lab_results' AND column_name = 'name') THEN
                ALTER TABLE lab_results ADD COLUMN name VARCHAR(100);
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'lab_results' AND column_name = 'lab_name') THEN
                ALTER TABLE lab_results ADD COLUMN lab_name VARCHAR(100);
            END IF;
        END $$;
    """)
    
    # Копируем данные обратно
    op.execute("""
        UPDATE lab_results 
        SET name = test_type 
        WHERE name IS NULL AND test_type IS NOT NULL;
    """)
    
    # Удаляем новые колонки
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'lab_results' AND column_name = 'test_type') THEN
                ALTER TABLE lab_results DROP COLUMN test_type;
            END IF;
        END $$;
    """)
    
    # Делаем старые колонки обязательными
    op.execute("""
        ALTER TABLE lab_results ALTER COLUMN name SET NOT NULL;
    """) 