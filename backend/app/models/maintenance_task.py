import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

MAINTENANCE_TYPES = ("preventivo", "correctivo")
SCHEDULED_BY_OPTIONS = ("tiempo", "km")
MAINTENANCE_TASK_STATUSES = ("pendiente", "en_proceso", "completada", "vencida", "cancelada")


class MaintenanceTask(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "maintenance_tasks"
    __table_args__ = (
        CheckConstraint(f"type IN {MAINTENANCE_TYPES}", name="ck_maintenance_tasks_type"),
        CheckConstraint(f"scheduled_by IN {SCHEDULED_BY_OPTIONS}", name="ck_maintenance_tasks_scheduled_by"),
        CheckConstraint(f"status IN {MAINTENANCE_TASK_STATUSES}", name="ck_maintenance_tasks_status"),
        CheckConstraint(
            "(scheduled_by = 'tiempo' AND due_date IS NOT NULL) "
            "OR (scheduled_by = 'km' AND due_km IS NOT NULL)",
            name="ck_maintenance_tasks_due_matches_scheduled_by",
        ),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    scheduled_by: Mapped[str] = mapped_column(String(10), nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pendiente")
    responsible_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")

    vehicle: Mapped["Vehicle"] = relationship(back_populates="maintenance_tasks")
    records: Mapped[list["MaintenanceRecord"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )
