"""add_workout_type_column

Revision ID: 0e19b26b20e3
Revises: 9cfaeaedd9b7
Create Date: 2025-09-01 12:56:21.152358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e19b26b20e3'
down_revision: Union[str, None] = '9cfaeaedd9b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
