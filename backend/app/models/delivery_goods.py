import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

DELIVERY_GOODS_MOVEMENT_TYPES = ("entrada", "salida", "ajuste")


class DeliveryGoods(Base, UUIDPKMixin, TimestampMixin):
    """Catálogo de mercancía de reparto (Fase 9A) — distinto del inventario de repuestos (Fase 6):
    esto es carga de clientes que se reparte, con peso/volumen por unidad para el CVRP de 9C. Mismo
    patrón de stock derivado que `inventory_items`: `quantity` solo se modifica vía movimientos."""

    __tablename__ = "delivery_goods"
    __table_args__ = (UniqueConstraint("company_id", "sku", name="uq_delivery_goods_company_sku"),)

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
    # Peso/volumen por unidad — alimentan la demanda de cada parada en el CVRP (Fase 9C).
    weight_kg_per_unit: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False, default=0)
    volume_m3_per_unit: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False, default=0)
    custom_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")


class DeliveryGoodsMovement(Base, UUIDPKMixin):
    """Bitácora de stock de la mercancía de reparto — mismo patrón que `inventory_movements`
    (Fase 6): entrada/salida/ajuste, `apply_movement` atómico garantiza quantity no-negativa."""

    __tablename__ = "delivery_goods_movements"
    __table_args__ = (
        CheckConstraint(
            f"movement_type IN {DELIVERY_GOODS_MOVEMENT_TYPES}", name="ck_delivery_goods_movements_type"
        ),
        CheckConstraint("quantity <> 0", name="ck_delivery_goods_movements_quantity_nonzero"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    goods_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("delivery_goods.id", ondelete="CASCADE"), nullable=False
    )
    movement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    unit_cost: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    reference_doc: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
