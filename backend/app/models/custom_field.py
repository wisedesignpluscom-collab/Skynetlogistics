import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

# Entidades cuyo formulario admite campos custom (Config-A). Cada una tiene una columna
# `custom_data` JSONB donde se guardan los valores. Ampliar esta tupla + agregar la columna a la
# tabla correspondiente para habilitar una entidad nueva.
CUSTOM_FIELD_ENTITY_TYPES = (
    "vehicle",
    "driver",
    "trip",
    "delivery_order",
    "client",
    "maintenance_task",
    "inventory_item",
    "tire",
    "delivery_goods",
)
CUSTOM_FIELD_TYPES = ("texto", "numero", "fecha", "select", "checkbox", "area_texto")


class CustomFieldDefinition(Base, UUIDPKMixin, TimestampMixin):
    """Definición de un campo custom que un admin agrega al formulario de una entidad, por empresa
    (Config-A del módulo de configuración sin código). Los valores viven en la columna `custom_data`
    (JSONB) de cada entidad, indexados por `key`."""

    __tablename__ = "custom_field_definitions"
    __table_args__ = (
        UniqueConstraint("company_id", "entity_type", "key", name="uq_custom_fields_company_entity_key"),
        CheckConstraint(f"entity_type IN {CUSTOM_FIELD_ENTITY_TYPES}", name="ck_custom_fields_entity_type"),
        CheckConstraint(f"field_type IN {CUSTOM_FIELD_TYPES}", name="ck_custom_fields_field_type"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    key: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(150), nullable=False)
    field_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # [{"value": "...", "label": "..."}] — solo para field_type="select".
    options: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    help_text: Mapped[str | None] = mapped_column(Text, nullable=True)
