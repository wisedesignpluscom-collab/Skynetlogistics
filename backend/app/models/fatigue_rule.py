import uuid

from sqlalchemy import ForeignKey, Numeric, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class FatigueRule(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "fatigue_rules"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    max_continuous_hours: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=4.5)
    max_24h_hours: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=10.0)
    max_7day_hours: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=60.0)
    night_driving_weight: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=1.5)
    night_start_hour: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=22)
    night_end_hour: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=5)
