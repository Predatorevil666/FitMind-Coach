"""add_meal_quantity_unit

Revision ID: 3598d34ff2b9
Revises: dc028814a769
Create Date: 2025-09-01 12:37:30.823513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3598d34ff2b9'
down_revision: Union[str, None] = 'dc028814a769'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
