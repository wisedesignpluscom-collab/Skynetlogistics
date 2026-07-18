import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin
from app.models.vehicle import VEHICLE_TYPES


class RateTable(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "rate_tables"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "origin",
            "destination",
            "vehicle_type",
            "cargo_type",
            name="uq_rate_tables_route",
        ),
        CheckConstraint(f"vehicle_type IN {VEHICLE_TYPES}", name="ck_rate_tables_vehicle_type"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    origin: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(20), nullable=False)
    cargo_type: Mapped[str] = mapped_column(String(100), nullable=False)
    distance_km: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    freight_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
