import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

DRIVER_STATUSES = ("activo", "suspendido", "inactivo")


class Driver(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "drivers"
    __table_args__ = (
        UniqueConstraint("company_id", "license_number", name="uq_drivers_company_license"),
        CheckConstraint(f"status IN {DRIVER_STATUSES}", name="ck_drivers_status"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    license_number: Mapped[str] = mapped_column(String(50), nullable=False)
    license_expiry: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="activo")
