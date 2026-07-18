import uuid

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class TireSettings(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "tire_settings"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    disparity_threshold_mm: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False, default=3.0)
