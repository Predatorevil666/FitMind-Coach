"""fix_column_names_sql

Revision ID: f5eb1d1f3377
Revises: 3598d34ff2b9
Create Date: 2025-09-01 12:45:09.213714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5eb1d1f3377'
down_revision: Union[str, None] = '3598d34ff2b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
