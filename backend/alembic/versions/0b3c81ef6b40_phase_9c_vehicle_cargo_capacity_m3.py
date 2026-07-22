"""phase 9c vehicle cargo capacity m3

Revision ID: 0b3c81ef6b40
Revises: 3be1041184dd
Create Date: 2026-07-20 18:01:07.262343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0b3c81ef6b40'
down_revision: Union[str, None] = '3be1041184dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTA: se omiten las particiones mensuales de vehicle_positions (runtime, no metadata) — mismo
    # criterio que las migraciones de Fase 8/9A/9B.
    op.add_column('vehicles', sa.Column('cargo_capacity_m3', sa.Numeric(precision=10, scale=3), nullable=True))


def downgrade() -> None:
    op.drop_column('vehicles', 'cargo_capacity_m3')
