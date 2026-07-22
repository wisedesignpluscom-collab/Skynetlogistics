import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.crud import custom_field as custom_field_crud
from app.crud import form_rule as form_rule_crud
from app.models.custom_field import CUSTOM_FIELD_ENTITY_TYPES
from app.models.user import User
from app.schemas.form_rule import (
    EntityFieldOut,
    EntitySchemaOut,
    FormRuleCreate,
    FormRuleOut,
    FormRuleUpdate,
)
from app.services.entity_fields import system_fields_for

router = APIRouter(prefix="/form-rules", tags=["config"])


@router.get("/entity-schema", response_model=EntitySchemaOut)
async def get_entity_schema(
    entity_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EntitySchemaOut:
    """Campos "reglables" de una entidad: los de sistema (catálogo) + los custom activos. Alimenta
    el editor de reglas y la evaluación en vivo. No exige `config` (cualquiera que edita la entidad
    necesita conocer sus campos)."""
    if entity_type not in CUSTOM_FIELD_ENTITY_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "entity_type no soportado")

    fields: list[EntityFieldOut] = [
        EntityFieldOut(**f, source="sistema") for f in system_fields_for(entity_type)
    ]
    custom = await custom_field_crud.list_for_entity(db, current_user.company_id, entity_type, only_active=True)
    for c in custom:
        fields.append(
            EntityFieldOut(
                key=f"custom.{c.key}", label=c.label, type=c.field_type, options=c.options, source="custom"
            )
        )
    return EntitySchemaOut(entity_type=entity_type, fields=fields)


@router.get("", response_model=list[FormRuleOut])
async def list_form_rules(
    entity_type: str,
    kind: str | None = None,
    only_active: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FormRuleOut]:
    if entity_type not in CUSTOM_FIELD_ENTITY_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "entity_type no soportado")
    return await form_rule_crud.list_for_entity(
        db, current_user.company_id, entity_type, kind=kind, only_active=only_active
    )


@router.post("", response_model=FormRuleOut, status_code=status.HTTP_201_CREATED)
async def create_form_rule(
    payload: FormRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config", "write")),
) -> FormRuleOut:
    return await form_rule_crud.create(db, current_user.company_id, payload)


@router.patch("/{rule_id}", response_model=FormRuleOut)
async def update_form_rule(
    rule_id: uuid.UUID,
    payload: FormRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config", "write")),
) -> FormRuleOut:
    rule = await form_rule_crud.get(db, rule_id, current_user.company_id)
    if rule is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Regla no encontrada")
    return await form_rule_crud.update(db, rule, payload)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_form_rule(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config", "delete")),
) -> None:
    rule = await form_rule_crud.get(db, rule_id, current_user.company_id)
    if rule is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Regla no encontrada")
    await form_rule_crud.delete(db, rule)
