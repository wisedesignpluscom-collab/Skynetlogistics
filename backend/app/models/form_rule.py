import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin
from app.models.custom_field import CUSTOM_FIELD_ENTITY_TYPES

# Reutiliza el mismo catálogo de entidades que los campos custom (Config-A).
FORM_RULE_KINDS = ("formulario", "validacion")
# Acciones de regla de formulario: mostrar/ocultar/requerir/opcional/calcular. La de validación
# usa "bloquear". Se validan en el schema; el modelo solo guarda el JSONB.
FORM_RULE_ACTION_TYPES = ("mostrar", "ocultar", "requerir", "opcional", "calcular", "bloquear")


class FormRule(Base, UUIDPKMixin, TimestampMixin):
    """Regla sin código (Config-B): cuando `condition` se cumple, se aplican `actions`.
    `kind='formulario'` -> se evalúa en vivo en el cliente (mostrar/ocultar/requerir/calcular);
    `kind='validacion'` -> se evalúa en el backend al guardar (bloquear con mensaje)."""

    __tablename__ = "form_rules"
    __table_args__ = (
        CheckConstraint(f"entity_type IN {CUSTOM_FIELD_ENTITY_TYPES}", name="ck_form_rules_entity_type"),
        CheckConstraint(f"kind IN {FORM_RULE_KINDS}", name="ck_form_rules_kind"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    kind: Mapped[str] = mapped_column(String(15), nullable=False)
    # {"match": "all"|"any", "conditions": [{"field", "op", "value"}]}
    condition: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # formulario: [{"type", "target", "formula"?}]  | validacion: [{"type": "bloquear", "message"}]
    actions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
