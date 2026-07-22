import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

DRIVER_STATUSES = ("activo", "suspendido", "inactivo")
PAY_PERIODS = ("semanal", "quincenal", "mensual")


class Driver(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "drivers"
    __table_args__ = (
        UniqueConstraint("company_id", "license_number", name="uq_drivers_company_license"),
        CheckConstraint(f"status IN {DRIVER_STATUSES}", name="ck_drivers_status"),
        CheckConstraint(f"pay_period IS NULL OR pay_period IN {PAY_PERIODS}", name="ck_drivers_pay_period"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    license_number: Mapped[str] = mapped_column(String(50), nullable=False)
    license_expiry: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="activo")
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    secondary_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_salary: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    pay_period: Mapped[str | None] = mapped_column(String(20), nullable=True)
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    termination_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=True
    )
    custom_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
