"""merge_heads

Revision ID: 2118bbfa414c
Revises: c7c3cb1f9a21, fix_goal_type
Create Date: 2025-09-01 12:35:52.579199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2118bbfa414c'
down_revision: Union[str, None] = ('c7c3cb1f9a21', 'fix_goal_type')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
