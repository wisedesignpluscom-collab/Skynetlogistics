"""expand inventory_movements with provider, invoice and tax fields

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-07-20 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('inventory_movements', sa.Column('provider_id', sa.UUID(), nullable=True))
    op.add_column('inventory_movements', sa.Column('invoice_number', sa.String(length=100), nullable=True))
    op.add_column(
        'inventory_movements', sa.Column('tax_percentage', sa.Numeric(precision=5, scale=2), nullable=True)
    )
    op.create_foreign_key(
        'fk_inventory_movements_provider_id', 'inventory_movements', 'providers', ['provider_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_inventory_movements_provider_id', 'inventory_movements', type_='foreignkey')
    op.drop_column('inventory_movements', 'tax_percentage')
    op.drop_column('inventory_movements', 'invoice_number')
    op.drop_column('inventory_movements', 'provider_id')
