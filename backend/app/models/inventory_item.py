import uuid

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class InventoryItem(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "inventory_items"
    __table_args__ = (UniqueConstraint("company_id", "sku", name="uq_inventory_items_company_sku"),)

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False
    )
    sku: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="unidad")
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    min_stock: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    unit_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    custom_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
