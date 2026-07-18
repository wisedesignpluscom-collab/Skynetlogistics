import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDPKMixin
from app.models.tire import AXLE_DUAL_POSITIONS, AXLE_SIDES

TIRE_MOVEMENT_TYPES = (
    "instalacion",
    "desinstalacion",
    "envio_reparacion",
    "envio_reencauche",
    "retorno_taller",
)


class TireMovement(Base, UUIDPKMixin):
    __tablename__ = "tire_movements"
    __table_args__ = (
        CheckConstraint(f"movement_type IN {TIRE_MOVEMENT_TYPES}", name="ck_tire_movements_type"),
        CheckConstraint(f"axle_side IN {AXLE_SIDES}", name="ck_tire_movements_axle_side"),
        CheckConstraint(
            f"axle_dual_position IN {AXLE_DUAL_POSITIONS}", name="ck_tire_movements_axle_dual_position"
        ),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    tire_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tires.id", ondelete="CASCADE"), nullable=False
    )
    movement_type: Mapped[str] = mapped_column(String(20), nullable=False)

    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True
    )
    axle_number: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    axle_side: Mapped[str | None] = mapped_column(String(10), nullable=True)
    axle_dual_position: Mapped[str | None] = mapped_column(String(10), nullable=True)
    warehouse_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True
    )
    provider_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("providers.id"), nullable=True
    )

    km_at_movement: Mapped[int | None] = mapped_column(Integer, nullable=True)
    thickness_mm: Mapped[float | None] = mapped_column(Numeric(4, 1), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
