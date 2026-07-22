"""expand companies with contact/address fields

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-20 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('companies', sa.Column('contact_person', sa.String(length=255), nullable=True))
    op.add_column('companies', sa.Column('phone', sa.String(length=30), nullable=True))
    op.add_column('companies', sa.Column('mobile_phone', sa.String(length=30), nullable=True))
    op.add_column('companies', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('companies', sa.Column('address', sa.String(length=500), nullable=True))
    op.add_column('companies', sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('companies', sa.Column('state', sa.String(length=100), nullable=True))
    op.add_column('companies', sa.Column('country', sa.String(length=100), nullable=True))
    op.add_column('companies', sa.Column('logo_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('companies', 'logo_url')
    op.drop_column('companies', 'country')
    op.drop_column('companies', 'state')
    op.drop_column('companies', 'city')
    op.drop_column('companies', 'address')
    op.drop_column('companies', 'email')
    op.drop_column('companies', 'mobile_phone')
    op.drop_column('companies', 'phone')
    op.drop_column('companies', 'contact_person')
