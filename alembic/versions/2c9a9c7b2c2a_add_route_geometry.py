"""add_route_geometry

Revision ID: 2c9a9c7b2c2a
Revises: b7a2f6c3d9e1
Create Date: 2026-02-05 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c9a9c7b2c2a'
down_revision: Union[str, Sequence[str], None] = 'b7a2f6c3d9e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('routes', sa.Column('geometry', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('routes', 'geometry')
