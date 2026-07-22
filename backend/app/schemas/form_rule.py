import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.custom_field import CUSTOM_FIELD_ENTITY_TYPES
from app.models.form_rule import FORM_RULE_KINDS
from app.services.rule_engine import CONDITION_OPS

_FORM_ACTION_TYPES = ("mostrar", "ocultar", "requerir", "opcional", "calcular")


class RuleConditionItem(BaseModel):
    field: str = Field(min_length=1, max_length=100)
    op: str = Field(pattern="^(" + "|".join(CONDITION_OPS) + ")$")
    value: Any = None


class RuleCondition(BaseModel):
    match: str = Field(default="all", pattern="^(all|any)$")
    conditions: list[RuleConditionItem] = Field(default_factory=list)


class RuleAction(BaseModel):
    type: str
    target: str | None = Field(default=None, max_length=100)  # campo objetivo (reglas de formulario)
    formula: str | None = Field(default=None, max_length=500)  # solo type="calcular"
    message: str | None = Field(default=None, max_length=500)  # solo type="bloquear"


class FormRuleBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    condition: RuleCondition = Field(default_factory=RuleCondition)
    actions: list[RuleAction] = Field(default_factory=list)
    active: bool = True
    order: int = 0


class FormRuleCreate(FormRuleBase):
    entity_type: str = Field(pattern="^(" + "|".join(CUSTOM_FIELD_ENTITY_TYPES) + ")$")
    kind: str = Field(pattern="^(" + "|".join(FORM_RULE_KINDS) + ")$")

    @model_validator(mode="after")
    def _validate_actions_for_kind(self) -> "FormRuleCreate":
        if not self.actions:
            raise ValueError("La regla necesita al menos una acción")
        if self.kind == "validacion":
            for a in self.actions:
                if a.type != "bloquear":
                    raise ValueError("Una regla de validación solo admite la acción 'bloquear'")
                if not (a.message and a.message.strip()):
                    raise ValueError("La acción 'bloquear' requiere un mensaje")
        else:  # formulario
            for a in self.actions:
                if a.type not in _FORM_ACTION_TYPES:
                    raise ValueError(f"Acción de formulario inválida: {a.type}")
                if not a.target:
                    raise ValueError("Las acciones de formulario requieren un campo objetivo")
                if a.type == "calcular" and not (a.formula and a.formula.strip()):
                    raise ValueError("La acción 'calcular' requiere una fórmula")
        return self


class FormRuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    condition: RuleCondition | None = None
    actions: list[RuleAction] | None = None
    active: bool | None = None
    order: int | None = None


class FormRuleOut(FormRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    entity_type: str
    kind: str
    created_at: datetime
    updated_at: datetime


class EntityFieldOut(BaseModel):
    key: str
    label: str
    type: str
    options: list[dict] = Field(default_factory=list)
    source: str  # "sistema" | "custom"


class EntitySchemaOut(BaseModel):
    entity_type: str
    fields: list[EntityFieldOut]
