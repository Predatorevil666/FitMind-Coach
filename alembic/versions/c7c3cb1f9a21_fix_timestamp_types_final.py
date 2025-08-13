"""fix_timestamp_types_final

Revision ID: c7c3cb1f9a21
Revises: c7e629ccf495
Create Date: 2025-08-13 16:00:01.467661

"""

from collections.abc import Sequence
from typing import Union

# revision identifiers, used by Alembic.
revision: str = "c7c3cb1f9a21"
down_revision: Union[str, None] = "c7e629ccf495"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
