"""vehicle owners, vehicle documents, and expanded vehicle fields

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-07-20 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'vehicle_owners',
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('contact_person', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=30), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.String(length=2000), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'vehicle_document_types',
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('alert_days_before', sa.SmallInteger(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'name', name='uq_vehicle_document_types_company_name'),
    )
    op.create_table(
        'vehicle_documents',
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('vehicle_id', sa.UUID(), nullable=False),
        sa.Column('document_type_id', sa.UUID(), nullable=False),
        sa.Column('number', sa.String(length=100), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_type_id'], ['vehicle_document_types.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.add_column('vehicles', sa.Column('owner_id', sa.UUID(), nullable=True))
    op.add_column('vehicles', sa.Column('color', sa.String(length=50), nullable=True))
    op.add_column('vehicles', sa.Column('engine_serial', sa.String(length=100), nullable=True))
    op.add_column('vehicles', sa.Column('has_odometer', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column('vehicles', sa.Column('odometer_digits', sa.SmallInteger(), nullable=True))
    op.add_column('vehicles', sa.Column('cargo_capacity_kg', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('vehicles', sa.Column('contract', sa.String(length=255), nullable=True))
    op.create_foreign_key('fk_vehicles_owner_id', 'vehicles', 'vehicle_owners', ['owner_id'], ['id'])
    op.alter_column('vehicles', 'has_odometer', server_default=None)


def downgrade() -> None:
    op.drop_constraint('fk_vehicles_owner_id', 'vehicles', type_='foreignkey')
    op.drop_column('vehicles', 'contract')
    op.drop_column('vehicles', 'cargo_capacity_kg')
    op.drop_column('vehicles', 'odometer_digits')
    op.drop_column('vehicles', 'has_odometer')
    op.drop_column('vehicles', 'engine_serial')
    op.drop_column('vehicles', 'color')
    op.drop_column('vehicles', 'owner_id')
    op.drop_table('vehicle_documents')
    op.drop_table('vehicle_document_types')
    op.drop_table('vehicle_owners')
