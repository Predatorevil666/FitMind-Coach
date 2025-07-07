"""merge_heads

Revision ID: b97475dc6cb6
Revises: add_telegram_id, fix_datetime_utcnow
Create Date: 2025-07-07 18:21:48.741093

"""

from collections.abc import Sequence
from typing import Union

# revision identifiers, used by Alembic.
revision: str = "b97475dc6cb6"
down_revision: Union[str, None] = ("add_telegram_id", "fix_datetime_utcnow")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
