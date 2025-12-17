"""Add vehicles and vehicles_users tables

Revision ID: 2e37c0074375
Revises: 7c38b3f35c6d
Create Date: 2025-12-17 05:33:51.982875

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2e37c0074375"
down_revision: Union[str, Sequence[str], None] = "7c38b3f35c6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create vehicles table
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plate_number", sa.String(length=20), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("is_sharing_location", sa.Boolean(), default=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plate_number"),
    )

    # Create vehicles_users table
    op.create_table(
        "vehicles_users",
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=11), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.public_id"]),
        sa.PrimaryKeyConstraint("vehicle_id", "user_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("vehicles_users")
    op.drop_table("vehicles")
