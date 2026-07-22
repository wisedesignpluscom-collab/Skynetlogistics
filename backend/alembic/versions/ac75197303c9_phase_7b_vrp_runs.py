"""phase 7b vrp runs

Revision ID: ac75197303c9
Revises: a7b8c9d0e1f2
Create Date: 2026-07-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ac75197303c9'
down_revision: Union[str, None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'vrp_runs',
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('input_stops', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('cargo_type', sa.String(length=100), nullable=False),
        sa.Column('vehicle_ids_considered', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('proposed_assignment', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('result_trip_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.CheckConstraint("status IN ('propuesto', 'confirmado', 'descartado')", name='ck_vrp_runs_status'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('vrp_runs')
