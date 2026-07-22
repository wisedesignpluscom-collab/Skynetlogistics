import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin
from app.models.custom_field import CUSTOM_FIELD_ENTITY_TYPES

# Reutiliza el mismo catálogo de entidades que campos custom (Config-A) y reglas (Config-B).
WORKFLOW_EVENTS = ("creado", "actualizado", "cambio_estado")
# Acciones soportadas en la primera versión (Config-C): crear una alerta para el despachador, o
# fijar el valor de un campo custom de la propia entidad. Se validan en el schema.
WORKFLOW_ACTION_TYPES = ("crear_alerta", "actualizar_campo")


class Workflow(Base, UUIDPKMixin, TimestampMixin):
    """Automatización sin código (Config-C): cuando ocurre `event` sobre una entidad y `condition`
    se cumple (evaluada sobre el registro YA guardado), se ejecutan `actions` — a diferencia de las
    reglas de Config-B (que actúan mientras se llena el formulario o bloquean antes de guardar),
    esto corre DESPUÉS de persistir, como efecto secundario best-effort."""

    __tablename__ = "workflows"
    __table_args__ = (
        CheckConstraint(f"entity_type IN {CUSTOM_FIELD_ENTITY_TYPES}", name="ck_workflows_entity_type"),
        CheckConstraint(f"event IN {WORKFLOW_EVENTS}", name="ck_workflows_event"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    event: Mapped[str] = mapped_column(String(20), nullable=False)
    # {"match": "all"|"any", "conditions": [{"field", "op", "value"}]} — mismo evaluador de Config-B.
    condition: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # [{"type": "crear_alerta", "message", "severity"} | {"type": "actualizar_campo", "target", "value"}]
    actions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
