import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

RISK_LEVELS = ("bajo", "medio", "alto", "critico")


class DriverFatigueLog(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "driver_fatigue_logs"
    __table_args__ = (
        UniqueConstraint("driver_id", "date", name="uq_driver_fatigue_logs_driver_date"),
        CheckConstraint(f"risk_level IN {RISK_LEVELS}", name="ck_driver_fatigue_logs_risk_level"),
        Index("ix_driver_fatigue_logs_driver_date", "driver_id", "date"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    continuous_driving_min: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_24h_min: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_7day_min: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    night_driving_min: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(10), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
