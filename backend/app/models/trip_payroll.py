import uuid

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class TripPayroll(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "trip_payroll"

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    base_salary: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    meal_allowance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    holiday_bonus: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    return_bonus: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    bonuses: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    advance_payment: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    total_to_pay: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    trip: Mapped["Trip"] = relationship(back_populates="payroll")
