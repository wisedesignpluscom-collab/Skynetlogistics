import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDPKMixin
from sqlalchemy import func


class MaintenanceRecord(Base, UUIDPKMixin):
    __tablename__ = "maintenance_records"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("maintenance_tasks.id", ondelete="CASCADE"), nullable=False
    )
    cost_labor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    cost_parts: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    provider_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("providers.id"), nullable=True
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task: Mapped["MaintenanceTask"] = relationship(back_populates="records")
