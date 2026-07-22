import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.custom_field import CUSTOM_FIELD_ENTITY_TYPES
from app.models.workflow import WORKFLOW_EVENTS
from app.schemas.form_rule import RuleCondition

_ALERT_SEVERITIES = ("baja", "media", "alta")


class WorkflowAction(BaseModel):
    type: str
    # crear_alerta:
    message: str | None = Field(default=None, max_length=500)
    severity: str | None = Field(default=None, pattern="^(" + "|".join(_ALERT_SEVERITIES) + ")$")
    # actualizar_campo:
    target: str | None = Field(default=None, max_length=100)
    value: str | float | bool | None = None


class WorkflowBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    condition: RuleCondition = Field(default_factory=RuleCondition)
    actions: list[WorkflowAction] = Field(default_factory=list)
    active: bool = True
    order: int = 0


class WorkflowCreate(WorkflowBase):
    entity_type: str = Field(pattern="^(" + "|".join(CUSTOM_FIELD_ENTITY_TYPES) + ")$")
    event: str = Field(pattern="^(" + "|".join(WORKFLOW_EVENTS) + ")$")

    @model_validator(mode="after")
    def _validate_actions(self) -> "WorkflowCreate":
        if not self.actions:
            raise ValueError("El workflow necesita al menos una acción")
        for a in self.actions:
            if a.type == "crear_alerta":
                if not (a.message and a.message.strip()):
                    raise ValueError("La acción 'crear_alerta' requiere un mensaje")
            elif a.type == "actualizar_campo":
                if not a.target:
                    raise ValueError("La acción 'actualizar_campo' requiere un campo objetivo")
                if not a.target.startswith("custom."):
                    raise ValueError("'actualizar_campo' solo puede fijar campos custom (custom.<key>)")
            else:
                raise ValueError(f"Acción de workflow inválida: {a.type}")
        return self


class WorkflowUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    condition: RuleCondition | None = None
    actions: list[WorkflowAction] | None = None
    active: bool | None = None
    order: int | None = None


class WorkflowOut(WorkflowBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    entity_type: str
    event: str
    created_at: datetime
    updated_at: datetime
