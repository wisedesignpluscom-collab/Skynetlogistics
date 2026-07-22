"""maintenance settings for semaforo thresholds

Revision ID: a1b2c3d4e5f6
Revises: 917b61b36bbd
Create Date: 2026-07-19 09:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '917b61b36bbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'maintenance_settings',
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('warning_days_threshold', sa.Integer(), nullable=False),
        sa.Column('warning_km_threshold', sa.Integer(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id'),
    )


def downgrade() -> None:
    op.drop_table('maintenance_settings')
