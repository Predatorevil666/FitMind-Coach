"""rename_type_columns

Revision ID: dc028814a769
Revises: 2118bbfa414c
Create Date: 2025-09-01 12:36:09.001739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc028814a769'
down_revision: Union[str, None] = '2118bbfa414c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
