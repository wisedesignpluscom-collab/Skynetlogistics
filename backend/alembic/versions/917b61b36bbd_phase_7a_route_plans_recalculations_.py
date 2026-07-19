"""phase 7a route plans recalculations settings

Revision ID: 917b61b36bbd
Revises: f609f20b1c1d
Create Date: 2026-07-19 03:42:56.898347

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '917b61b36bbd'
down_revision: Union[str, None] = 'f609f20b1c1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTA: se removieron del autogenerate los drop/create de las particiones mensuales de
    # vehicle_positions (y2026m07/08/09) — son tablas creadas por SQL crudo en la migración de
    # Fase 3, no son parte de los metadatos de SQLAlchemy, y Alembic las detecta erróneamente
    # como "removidas". Mismo patrón que las migraciones de Fase 4, 5 y 6.
    op.create_table(
        'route_settings',
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('deviation_threshold_m', sa.Integer(), nullable=False),
        sa.Column('recalc_cooldown_min', sa.Integer(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id'),
    )
    op.create_table(
        'route_plans',
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('trip_id', sa.UUID(), nullable=False),
        sa.Column('origin_lat', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('origin_lng', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('destination_lat', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('destination_lng', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('geometry', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('waypoints', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('calculated_distance_km', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('calculated_duration_min', sa.Integer(), nullable=False),
        sa.Column('engine_used', sa.String(length=20), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('trip_id', name='uq_route_plans_trip'),
    )
    op.create_table(
        'route_recalculations',
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('route_plan_id', sa.UUID(), nullable=False),
        sa.Column('reason', sa.String(length=20), nullable=False),
        sa.Column('deviation_m', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('trigger_lat', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('trigger_lng', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('new_distance_km', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('new_duration_min', sa.Integer(), nullable=False),
        sa.Column('new_route_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.CheckConstraint("reason IN ('desvio', 'manual', 'trafico')", name='ck_route_recalculations_reason'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['route_plan_id'], ['route_plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('route_recalculations')
    op.drop_table('route_plans')
    op.drop_table('route_settings')
