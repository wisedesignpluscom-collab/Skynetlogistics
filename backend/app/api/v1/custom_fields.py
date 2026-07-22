import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.crud import custom_field as custom_field_crud
from app.models.custom_field import CUSTOM_FIELD_ENTITY_TYPES
from app.models.user import User
from app.schemas.custom_field import (
    CustomFieldDefinitionCreate,
    CustomFieldDefinitionOut,
    CustomFieldDefinitionUpdate,
)

router = APIRouter(prefix="/custom-fields", tags=["config"])


@router.get("", response_model=list[CustomFieldDefinitionOut])
async def list_custom_fields(
    entity_type: str,
    only_active: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CustomFieldDefinitionOut]:
    """Lista las definiciones de una entidad. NO exige permiso `config` (solo estar logueado):
    cualquier usuario que edita una entidad necesita conocer sus campos custom para renderizarlos.
    La administración (crear/editar/borrar) sí exige `config`."""
    if entity_type not in CUSTOM_FIELD_ENTITY_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "entity_type no soportado")
    return await custom_field_crud.list_for_entity(
        db, current_user.company_id, entity_type, only_active=only_active
    )


@router.post("", response_model=CustomFieldDefinitionOut, status_code=status.HTTP_201_CREATED)
async def create_custom_field(
    payload: CustomFieldDefinitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config", "write")),
) -> CustomFieldDefinitionOut:
    if payload.field_type == "select" and not payload.options:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Un campo 'select' requiere opciones")
    existing = await custom_field_crud.get_by_key(
        db, current_user.company_id, payload.entity_type, payload.key
    )
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un campo con esa clave en esta entidad")
    return await custom_field_crud.create(db, current_user.company_id, payload)


@router.patch("/{field_id}", response_model=CustomFieldDefinitionOut)
async def update_custom_field(
    field_id: uuid.UUID,
    payload: CustomFieldDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config", "write")),
) -> CustomFieldDefinitionOut:
    definition = await custom_field_crud.get(db, field_id, current_user.company_id)
    if definition is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Campo custom no encontrado")
    if definition.field_type == "select" and payload.options is not None and not payload.options:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Un campo 'select' requiere opciones")
    return await custom_field_crud.update(db, definition, payload)


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_field(
    field_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config", "delete")),
) -> None:
    definition = await custom_field_crud.get(db, field_id, current_user.company_id)
    if definition is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Campo custom no encontrado")
    await custom_field_crud.delete(db, definition)
