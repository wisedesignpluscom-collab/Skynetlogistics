import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin
from app.models.vehicle import VEHICLE_TYPES


class DriverPayRate(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "driver_pay_rates"
    __table_args__ = (
        UniqueConstraint("company_id", "vehicle_type", name="uq_driver_pay_rates_type"),
        CheckConstraint(f"vehicle_type IN {VEHICLE_TYPES}", name="ck_driver_pay_rates_vehicle_type"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    vehicle_type: Mapped[str] = mapped_column(String(20), nullable=False)
    daily_base_rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    meal_allowance_per_day: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    holiday_bonus_rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    return_bonus_rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
