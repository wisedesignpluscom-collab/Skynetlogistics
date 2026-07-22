"""config c workflows

Revision ID: c304a874ab13
Revises: 772cad34d9c4
Create Date: 2026-07-21 16:28:57.758042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c304a874ab13'
down_revision: Union[str, None] = '772cad34d9c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTA: se omiten las particiones mensuales de vehicle_positions (runtime, no metadata) — mismo
    # criterio que las migraciones de fases anteriores.
    op.create_table('workflows',
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('entity_type', sa.String(length=30), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('event', sa.String(length=20), nullable=False),
    sa.Column('condition', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('actions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("entity_type IN ('vehicle', 'driver', 'trip', 'delivery_order', 'client', 'maintenance_task', 'inventory_item', 'tire', 'delivery_goods')", name='ck_workflows_entity_type'),
    sa.CheckConstraint("event IN ('creado', 'actualizado', 'cambio_estado')", name='ck_workflows_event'),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('workflows')
