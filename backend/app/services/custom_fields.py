"""Validación de valores de campos custom (Config-A del módulo de configuración sin código).

Función pura (recibe las definiciones y el dict de valores, sin DB) — mismo criterio que el resto de
validaciones de negocio del proyecto: testeable con datos fijos. La usa cada endpoint de entidad al
crear/actualizar, para validar `custom_data` contra las definiciones activas de esa empresa+entidad.
"""

import uuid
from datetime import date
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import custom_field as custom_field_crud
from app.models.custom_field import CustomFieldDefinition


class CustomDataValidationError(ValueError):
    pass


async def validate_entity_custom_data(
    db: AsyncSession,
    company_id: uuid.UUID,
    entity_type: str,
    data: dict[str, Any] | None,
    *,
    payload: Any = None,
    existing: Any = None,
) -> dict[str, Any]:
    """Carga las definiciones activas de la entidad y valida `data` contra ellas, devolviendo el
    dict normalizado. Traduce el error de validación a un 422 — helper para los endpoints de las
    entidades habilitadas (vehículos, conductores, etc.).

    Si se pasa `payload` (el schema pydantic de create/update), además aplica las reglas de
    validación de Config-B (`kind='validacion'`): arma el contexto (campos de sistema + custom) y
    bloquea con 422 si alguna regla activa se cumple. `existing` (el registro actual, en update)
    completa el contexto con los campos no reenviados.
    """
    definitions = await custom_field_crud.list_for_entity(db, company_id, entity_type, only_active=True)
    try:
        clean = validate_custom_data(definitions, data)
    except CustomDataValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc

    if payload is not None:
        # Import local para evitar ciclo (form_rules no importa este módulo).
        from app.services.form_rules import apply_validation_rules, build_rule_context

        context = build_rule_context(entity_type, payload, clean, existing)
        await apply_validation_rules(db, company_id, entity_type, context)

    return clean


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def validate_custom_data(
    definitions: list[CustomFieldDefinition], data: dict[str, Any] | None
) -> dict[str, Any]:
    """Valida `data` contra `definitions` (las activas de la entidad) y devuelve un dict normalizado
    con SOLO las keys definidas (descarta las desconocidas). Lanza CustomDataValidationError si un
    campo requerido falta o un valor no calza con su tipo/opciones.
    """
    data = data or {}
    clean: dict[str, Any] = {}

    for definition in definitions:
        raw = data.get(definition.key)

        if _is_blank(raw):
            if definition.required:
                raise CustomDataValidationError(f"El campo '{definition.label}' es obligatorio")
            continue

        clean[definition.key] = _coerce_and_validate(definition, raw)

    return clean


def _coerce_and_validate(definition: CustomFieldDefinition, raw: Any) -> Any:
    field_type = definition.field_type
    label = definition.label

    if field_type in ("texto", "area_texto"):
        return str(raw)

    if field_type == "numero":
        try:
            return float(raw)
        except (TypeError, ValueError):
            raise CustomDataValidationError(f"El campo '{label}' debe ser numérico") from None

    if field_type == "checkbox":
        if isinstance(raw, bool):
            return raw
        if isinstance(raw, str) and raw.lower() in ("true", "false"):
            return raw.lower() == "true"
        raise CustomDataValidationError(f"El campo '{label}' debe ser verdadero/falso")

    if field_type == "fecha":
        try:
            date.fromisoformat(str(raw))
        except ValueError:
            raise CustomDataValidationError(
                f"El campo '{label}' debe ser una fecha válida (AAAA-MM-DD)"
            ) from None
        return str(raw)

    if field_type == "select":
        allowed = {o["value"] for o in definition.options}
        if str(raw) not in allowed:
            raise CustomDataValidationError(
                f"El valor de '{label}' no es una opción válida"
            )
        return str(raw)

    raise CustomDataValidationError(f"Tipo de campo desconocido: {field_type}")  # pragma: no cover
