import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDPKMixin

ALERT_SEVERITIES = ("baja", "media", "alta")
ALERT_STATUSES = ("no_leida", "leida")


class Alert(Base, UUIDPKMixin):
    __tablename__ = "alerts"
    __table_args__ = (
        CheckConstraint(f"severity IN {ALERT_SEVERITIES}", name="ck_alerts_severity"),
        CheckConstraint(f"status IN {ALERT_STATUSES}", name="ck_alerts_status"),
        Index(
            "uq_alerts_unread_dedupe",
            "company_id",
            "type",
            "entity_id",
            unique=True,
            postgresql_where=text("status = 'no_leida'"),
        ),
        Index("ix_alerts_company_status_created", "company_id", "status", "created_at"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="no_leida")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
