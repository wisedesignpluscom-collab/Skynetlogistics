import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, LargeBinary, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

INGESTION_MODES = ("webhook", "polling")


class GPSProvider(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "gps_providers"
    __table_args__ = (
        UniqueConstraint("company_id", "provider_name", name="uq_gps_providers_company_name"),
        CheckConstraint(f"ingestion_mode IN {INGESTION_MODES}", name="ck_gps_providers_ingestion_mode"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    adapter_type: Mapped[str] = mapped_column(String(50), nullable=False)
    api_credentials_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    ingestion_mode: Mapped[str] = mapped_column(String(10), nullable=False)
    webhook_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    polling_interval_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
