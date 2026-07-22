import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDPKMixin

CHAT_THREAD_STATUSES = ("abierto", "cerrado")
CHAT_MESSAGE_SENDER_TYPES = ("conductor", "despachador")


class ChatThread(Base, UUIDPKMixin):
    __tablename__ = "chat_threads"
    __table_args__ = (CheckConstraint(f"status IN {CHAT_THREAD_STATUSES}", name="ck_chat_threads_status"),)

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False
    )
    incident_report_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("incident_reports.id", ondelete="CASCADE"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="abierto")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChatMessage(Base, UUIDPKMixin):
    __tablename__ = "chat_messages"
    __table_args__ = (
        CheckConstraint(f"sender_type IN {CHAT_MESSAGE_SENDER_TYPES}", name="ck_chat_messages_sender_type"),
    )

    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_threads.id", ondelete="CASCADE"), nullable=False
    )
    sender_type: Mapped[str] = mapped_column(String(15), nullable=False)
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
