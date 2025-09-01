"""safe_rename_columns

Revision ID: 9cfaeaedd9b7
Revises: f5eb1d1f3377
Create Date: 2025-09-01 12:52:56.831287

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9cfaeaedd9b7'
down_revision: Union[str, None] = 'f5eb1d1f3377'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
