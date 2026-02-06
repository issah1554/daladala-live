"""add_vehicle_route_id

Revision ID: 3f4b9a2c1d7e
Revises: 2c9a9c7b2c2a
Create Date: 2026-02-06 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f4b9a2c1d7e'
down_revision: Union[str, Sequence[str], None] = '2c9a9c7b2c2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('vehicles', sa.Column('route_id', sa.BigInteger(), nullable=True))
    op.create_index('idx_vehicles_route', 'vehicles', ['route_id'], unique=False)
    op.create_foreign_key(
        'fk_vehicles_route',
        'vehicles',
        'routes',
        ['route_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_vehicles_route', 'vehicles', type_='foreignkey')
    op.drop_index('idx_vehicles_route', table_name='vehicles')
    op.drop_column('vehicles', 'route_id')
