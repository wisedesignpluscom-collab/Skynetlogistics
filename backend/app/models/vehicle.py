import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

VEHICLE_TYPES = ("camion", "remolque", "cabezal")
VEHICLE_STATUSES = ("activo", "taller", "inactivo")


class Vehicle(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "vehicles"
    __table_args__ = (
        UniqueConstraint("company_id", "plate", name="uq_vehicles_company_plate"),
        CheckConstraint(f"type IN {VEHICLE_TYPES}", name="ck_vehicles_type"),
        CheckConstraint(f"status IN {VEHICLE_STATUSES}", name="ck_vehicles_status"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    plate: Mapped[str] = mapped_column(String(20), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    vin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="activo")
    current_odometer_km: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    assigned_driver_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=True
    )

    assigned_driver: Mapped["Driver | None"] = relationship(foreign_keys=[assigned_driver_id])
    maintenance_tasks: Mapped[list["MaintenanceTask"]] = relationship(back_populates="vehicle")
