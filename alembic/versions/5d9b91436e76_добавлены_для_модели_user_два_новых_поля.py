"""Добавлены для модели User два новых поля

Revision ID: 5d9b91436e76
Revises: 537736d7f9f1
Create Date: 2026-07-27 21:33:19.067448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d9b91436e76'
down_revision: Union[str, Sequence[str], None] = '537736d7f9f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
