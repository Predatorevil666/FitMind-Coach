"""add_meal_quantity_unit

Revision ID: 3598d34ff2b9
Revises: dc028814a769
Create Date: 2025-09-01 12:37:30.823513

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3598d34ff2b9"
down_revision: Union[str, None] = "dc028814a769"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонки quantity и unit в таблицу meals
    op.add_column("meals", sa.Column("quantity", sa.Float(), nullable=True))
    op.add_column(
        "meals", sa.Column("unit", sa.String(length=50), nullable=True)
    )


def downgrade() -> None:
    # Удаляем добавленные колонки
    op.drop_column("meals", "unit")
    op.drop_column("meals", "quantity")
