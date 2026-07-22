"""Aplicación de reglas de validación al guardar (Config-B, lado backend).

Reglas `kind='validacion'`: si su condición se cumple para el registro que se está guardando,
bloquean con 422 y el mensaje configurado. Reutiliza el evaluador puro `rule_engine.evaluate_condition`
(mismo que la gemela TS aplica en vivo en el cliente para las reglas de formulario).

El contexto de evaluación combina los campos de SISTEMA "reglables" de la entidad (catálogo
`entity_fields.py`) con los campos custom aplanados como `custom.<key>`. En update se parte de los
valores del registro existente y se sobreescriben con lo que trae el payload parcial.
"""

import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import form_rule as form_rule_crud
from app.services.entity_fields import system_fields_for
from app.services.rule_engine import evaluate_condition


def build_rule_context(
    entity_type: str, payload: Any, clean_custom: dict | None, existing: Any | None
) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for field in system_fields_for(entity_type):
        key = field["key"]
        value = getattr(payload, key, None)
        if value is None and existing is not None:
            value = getattr(existing, key, None)
        context[key] = value

    custom: dict[str, Any] = {}
    if existing is not None:
        custom.update(getattr(existing, "custom_data", None) or {})
    if clean_custom is not None:
        custom.update(clean_custom)
    for k, v in custom.items():
        context[f"custom.{k}"] = v
    return context


async def apply_validation_rules(
    db: AsyncSession, company_id: uuid.UUID, entity_type: str, context: dict[str, Any]
) -> None:
    rules = await form_rule_crud.list_for_entity(
        db, company_id, entity_type, kind="validacion", only_active=True
    )
    for rule in rules:
        if evaluate_condition(rule.condition, context):
            for action in rule.actions:
                if action.get("type") == "bloquear":
                    raise HTTPException(
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                        action.get("message") or f"Registro bloqueado por la regla «{rule.name}»",
                    )
