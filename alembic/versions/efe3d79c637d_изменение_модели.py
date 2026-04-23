"""Изменение модели

Revision ID: efe3d79c637d
Revises: c4448a1f5352
Create Date: 2026-04-18 11:45:05.137444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efe3d79c637d'
down_revision: Union[str, Sequence[str], None] = 'c4448a1f5352'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
