"""phase 6 inventory items and movements

Revision ID: f609f20b1c1d
Revises: 689d55e81292
Create Date: 2026-07-19 03:07:10.549221

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f609f20b1c1d'
down_revision: Union[str, None] = '689d55e81292'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTA: se removieron del autogenerate los drop/create de las particiones mensuales de
    # vehicle_positions (y2026m07/08/09) — son tablas creadas por SQL crudo en la migración de
    # Fase 3, no son parte de los metadatos de SQLAlchemy, y Alembic las detecta erróneamente
    # como "removidas". Mismo patrón que las migraciones de Fase 4 y Fase 5.
    op.create_table('inventory_items',
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('warehouse_id', sa.UUID(), nullable=False),
    sa.Column('sku', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('unit', sa.String(length=20), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('min_stock', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('unit_cost', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('company_id', 'sku', name='uq_inventory_items_company_sku')
    )
    op.create_table('inventory_movements',
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('item_id', sa.UUID(), nullable=False),
    sa.Column('vehicle_id', sa.UUID(), nullable=True),
    sa.Column('movement_type', sa.String(length=20), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('unit_cost', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('reference_doc', sa.String(length=100), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('recorded_by', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.CheckConstraint("movement_type IN ('entrada', 'salida', 'ajuste')", name='ck_inventory_movements_type'),
    sa.CheckConstraint('quantity <> 0', name='ck_inventory_movements_quantity_nonzero'),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['item_id'], ['inventory_items.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['recorded_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('inventory_movements')
    op.drop_table('inventory_items')
