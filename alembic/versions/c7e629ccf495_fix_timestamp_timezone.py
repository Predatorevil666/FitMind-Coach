"""fix_timestamp_timezone

Revision ID: c7e629ccf495
Revises: b97475dc6cb6
Create Date: 2025-08-13 15:42:14.698619

"""

from collections.abc import Sequence
from typing import Union

# revision identifiers, used by Alembic.
revision: str = "c7e629ccf495"
down_revision: Union[str, None] = "b97475dc6cb6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
