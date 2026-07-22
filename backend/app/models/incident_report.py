import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

INCIDENT_TYPES = (
    "accidente",
    "siniestro",
    "averia_mecanica",
    "falta_viaticos",
    "multa",
    "retraso_via",
    "pernocte",
    "mercancia_danada",
    "retencion_aduana",
    "emergencia_salud",
    "otro",
)
INCIDENT_SEVERITIES = ("baja", "media", "alta", "critica")
INCIDENT_STATUSES = ("reportado", "en_atencion", "resuelto")


class IncidentReport(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "incident_reports"
    __table_args__ = (
        CheckConstraint(f"type IN {INCIDENT_TYPES}", name="ck_incident_reports_type"),
        CheckConstraint(f"severity IN {INCIDENT_SEVERITIES}", name="ck_incident_reports_severity"),
        CheckConstraint(f"status IN {INCIDENT_STATUSES}", name="ck_incident_reports_status"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True
    )
    trip_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(15), nullable=False, default="reportado")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    lng: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class IncidentReportAttachment(Base, UUIDPKMixin):
    __tablename__ = "incident_report_attachments"

    incident_report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("incident_reports.id", ondelete="CASCADE"), nullable=False
    )
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
