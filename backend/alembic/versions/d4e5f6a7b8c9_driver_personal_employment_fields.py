"""expand drivers with personal/employment fields

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-20 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('drivers', sa.Column('birth_date', sa.Date(), nullable=True))
    op.add_column('drivers', sa.Column('address', sa.String(length=500), nullable=True))
    op.add_column('drivers', sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('drivers', sa.Column('state', sa.String(length=100), nullable=True))
    op.add_column('drivers', sa.Column('country', sa.String(length=100), nullable=True))
    op.add_column('drivers', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('drivers', sa.Column('secondary_phone', sa.String(length=30), nullable=True))
    op.add_column('drivers', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('drivers', sa.Column('base_salary', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('drivers', sa.Column('pay_period', sa.String(length=20), nullable=True))
    op.add_column('drivers', sa.Column('hire_date', sa.Date(), nullable=True))
    op.add_column('drivers', sa.Column('termination_date', sa.Date(), nullable=True))
    op.create_check_constraint(
        'ck_drivers_pay_period', 'drivers', "pay_period IS NULL OR pay_period IN ('semanal', 'quincenal', 'mensual')"
    )


def downgrade() -> None:
    op.drop_constraint('ck_drivers_pay_period', 'drivers', type_='check')
    op.drop_column('drivers', 'termination_date')
    op.drop_column('drivers', 'hire_date')
    op.drop_column('drivers', 'pay_period')
    op.drop_column('drivers', 'base_salary')
    op.drop_column('drivers', 'notes')
    op.drop_column('drivers', 'secondary_phone')
    op.drop_column('drivers', 'email')
    op.drop_column('drivers', 'country')
    op.drop_column('drivers', 'state')
    op.drop_column('drivers', 'city')
    op.drop_column('drivers', 'address')
    op.drop_column('drivers', 'birth_date')
