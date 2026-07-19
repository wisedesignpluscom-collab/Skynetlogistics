import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDPKMixin

RECALCULATION_REASONS = ("desvio", "manual", "trafico")


class RouteRecalculation(Base, UUIDPKMixin):
    __tablename__ = "route_recalculations"
    __table_args__ = (
        CheckConstraint(f"reason IN {RECALCULATION_REASONS}", name="ck_route_recalculations_reason"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    route_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("route_plans.id", ondelete="CASCADE"), nullable=False
    )
    reason: Mapped[str] = mapped_column(String(20), nullable=False)
    deviation_m: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    trigger_lat: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    trigger_lng: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    new_distance_km: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    new_duration_min: Mapped[int] = mapped_column(Integer, nullable=False)
    new_route_data: Mapped[list] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
