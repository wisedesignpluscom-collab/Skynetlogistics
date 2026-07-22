import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

TIRE_STATUSES = ("instalado", "almacen", "reparacion")
AXLE_SIDES = ("izquierdo", "derecho", "unico")
AXLE_DUAL_POSITIONS = ("unico", "interior", "exterior")


class Tire(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "tires"
    __table_args__ = (
        UniqueConstraint("company_id", "unique_code", name="uq_tires_company_unique_code"),
        CheckConstraint(f"status IN {TIRE_STATUSES}", name="ck_tires_status"),
        CheckConstraint(f"axle_side IN {AXLE_SIDES}", name="ck_tires_axle_side"),
        CheckConstraint(f"axle_dual_position IN {AXLE_DUAL_POSITIONS}", name="ck_tires_axle_dual_position"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    unique_code: Mapped[str] = mapped_column(String(50), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    current_thickness_mm: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="almacen")

    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True
    )
    axle_number: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    axle_side: Mapped[str | None] = mapped_column(String(10), nullable=True)
    axle_dual_position: Mapped[str | None] = mapped_column(String(10), nullable=True)
    warehouse_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True
    )
    custom_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
