"""Motor de workflows (Config-C del módulo de configuración sin código).

A diferencia de las reglas de Config-B (que actúan mientras se llena el formulario o bloquean antes
de guardar), los workflows corren DESPUÉS de persistir un registro, como efecto secundario
best-effort — mismo criterio que el auto-trigger de ruteo en Fase 7A: si un workflow falla, no
revierte el guardado que ya ocurrió.

Reutiliza el evaluador puro de condiciones de Config-B (`rule_engine.evaluate_condition`) y el
catálogo de campos de sistema por entidad (`entity_fields.system_fields_for`).
"""

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import workflow as workflow_crud
from app.crud.alert import create_if_not_exists
from app.services.entity_fields import system_fields_for
from app.services.rule_engine import evaluate_condition

logger = logging.getLogger("app.jobs")

# Entidades cuyo endpoint de actualización genérico (PATCH) trae `status` en el payload, por lo que
# se les puede evaluar el evento `cambio_estado` ahí mismo. Otras entidades cambian de estado vía
# endpoints de transición especializados (ej. trips: start/close; delivery_orders: assign/deliver;
# tires: movements) — fuera de alcance de esta primera versión.
STATUS_UPDATABLE_ENTITIES = ("vehicle", "driver", "maintenance_task")


def _build_context(entity_type: str, entity: Any, *, previous_status: str | None = None) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for field in system_fields_for(entity_type):
        context[field["key"]] = getattr(entity, field["key"], None)
    for k, v in (getattr(entity, "custom_data", None) or {}).items():
        context[f"custom.{k}"] = v
    if previous_status is not None:
        context["previous_status"] = previous_status
    return context


async def run_workflows(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    entity_type: str,
    event: str,
    entity: Any,
    previous_status: str | None = None,
) -> None:
    """Evalúa los workflows activos de `entity_type`+`event` contra `entity` (ya persistido) y
    ejecuta las acciones de los que se cumplan. Nunca lanza — un fallo se loguea y se sigue con el
    resto, para no afectar la respuesta del endpoint que ya completó su guardado."""
    try:
        workflows = await workflow_crud.list_for_entity(
            db, company_id, entity_type, event=event, only_active=True
        )
    except Exception:  # noqa: BLE001
        logger.exception("No se pudieron cargar workflows de %s/%s", entity_type, event)
        return

    if not workflows:
        return

    context = _build_context(entity_type, entity, previous_status=previous_status)

    for wf in workflows:
        try:
            if not evaluate_condition(wf.condition, context):
                continue
            for action in wf.actions:
                await _run_action(db, company_id=company_id, entity_type=entity_type, entity=entity, wf_id=wf.id, wf_name=wf.name, action=action)
        except Exception:  # noqa: BLE001 — un workflow roto no debe tumbar el request
            logger.exception("Workflow %s (%s) falló al ejecutarse", wf.name, wf.id)


async def _run_action(
    db: AsyncSession, *, company_id: uuid.UUID, entity_type: str, entity: Any, wf_id: uuid.UUID, wf_name: str, action: dict
) -> None:
    action_type = action.get("type")

    if action_type == "crear_alerta":
        await create_if_not_exists(
            db,
            company_id=company_id,
            type=f"workflow_{wf_id}",
            entity_type=entity_type,
            entity_id=entity.id,
            message=action.get("message") or f"Workflow «{wf_name}»",
            severity=action.get("severity") or "media",
        )

    elif action_type == "actualizar_campo":
        target = action.get("target") or ""
        if not target.startswith("custom."):
            return
        key = target.removeprefix("custom.")
        current = dict(getattr(entity, "custom_data", None) or {})
        current[key] = action.get("value")
        entity.custom_data = current
        db.add(entity)
        await db.commit()
        await db.refresh(entity)
