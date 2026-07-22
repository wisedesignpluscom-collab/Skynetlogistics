import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class MaintenanceSettings(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "maintenance_settings"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    warning_days_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    warning_km_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=500)
