import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

TRIP_STATUSES = ("planificado", "en_curso", "completado", "cancelado")


class Trip(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "trips"
    __table_args__ = (
        CheckConstraint(f"status IN {TRIP_STATUSES}", name="ck_trips_status"),
        Index("ix_trips_company_status", "company_id", "status"),
        Index("ix_trips_vehicle_id", "vehicle_id"),
        Index("ix_trips_driver_id", "driver_id"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=False)
    trailer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True
    )
    origin: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    distance_km: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    cargo_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_round_trip: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="planificado")
    start_odometer_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_odometer_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    freight_cost: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    advance_payment: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    vehicle: Mapped["Vehicle"] = relationship(foreign_keys=[vehicle_id])
    trailer: Mapped["Vehicle | None"] = relationship(foreign_keys=[trailer_id])
    driver: Mapped["Driver"] = relationship()
    expenses: Mapped[list["TripExpense"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
    payroll: Mapped["TripPayroll | None"] = relationship(
        back_populates="trip", cascade="all, delete-orphan", uselist=False
    )
