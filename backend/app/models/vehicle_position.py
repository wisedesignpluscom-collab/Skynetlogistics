import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, PrimaryKeyConstraint, SmallInteger, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# Tabla particionada por rango de `timestamp` (mensual) — ver alembic/versions para el DDL
# de las particiones. El esquema es intencionalmente idéntico al que tendría una hypertable
# de TimescaleDB, para poder migrar a esa extensión más adelante sin tocar el modelo.


class VehiclePosition(Base):
    __tablename__ = "vehicle_positions"
    __table_args__ = (
        PrimaryKeyConstraint("id", "timestamp"),
        Index("ix_vehicle_positions_vehicle_ts", "vehicle_id", "timestamp"),
        Index("ix_vehicle_positions_company_ts", "company_id", "timestamp"),
        {"postgresql_partition_by": "RANGE (timestamp)"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    vehicle_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("gps_providers.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    lat: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    lng: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    speed_kmh: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    odometer_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ignition_status: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    heading: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
