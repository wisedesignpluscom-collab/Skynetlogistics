import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

# Ciclo de vida (Fase 9B):
#   pendiente --(asignar a trip: descuenta stock)--> asignado --> en_ruta --> entregado | fallido
# En 9C el confirm del VRP hará la asignación automática (llenar trip_id + status=asignado);
# en 9B la asignación es manual (el despachador elige un trip existente).
DELIVERY_ORDER_STATUSES = ("pendiente", "asignado", "en_ruta", "entregado", "fallido")


class DeliveryOrder(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "delivery_orders"
    __table_args__ = (
        CheckConstraint(f"status IN {DELIVERY_ORDER_STATUSES}", name="ck_delivery_orders_status"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    # trip que reparte este pedido — nullable hasta que se asigna (manual en 9B, VRP en 9C).
    trip_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    lat: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    lng: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    status: Mapped[str] = mapped_column(String(15), nullable=False, default="pendiente")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    time_window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    time_window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    delivery_proof_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    custom_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")

    items: Mapped[list["DeliveryOrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class DeliveryOrderItem(Base, UUIDPKMixin):
    __tablename__ = "delivery_order_items"

    delivery_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("delivery_orders.id", ondelete="CASCADE"), nullable=False
    )
    goods_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("delivery_goods.id"), nullable=False
    )
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    order: Mapped["DeliveryOrder"] = relationship(back_populates="items")
