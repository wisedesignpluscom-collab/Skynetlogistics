import uuid

from sqlalchemy import ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class DriverDocumentType(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "driver_document_types"
    __table_args__ = (UniqueConstraint("company_id", "name", name="uq_driver_document_types_company_name"),)

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    alert_days_before: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=60)
