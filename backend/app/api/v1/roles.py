import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import role as role_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.role import RoleCreate, RoleOut, RoleUpdate

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=Page[RoleOut])
async def list_roles(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles", "read")),
) -> Page[RoleOut]:
    items, total = await role_crud.list_paginated(
        db, company_id=current_user.company_id, page=page, page_size=page_size
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
async def create_role(
    payload: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles", "write")),
) -> RoleOut:
    if await role_crud.get_by_name(db, current_user.company_id, payload.name) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un rol con ese nombre en la empresa")
    return await role_crud.create(db, current_user.company_id, payload)


@router.get("/{role_id}", response_model=RoleOut)
async def get_role(
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles", "read")),
) -> RoleOut:
    role = await role_crud.get(db, role_id, current_user.company_id)
    if role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rol no encontrado")
    return role


@router.patch("/{role_id}", response_model=RoleOut)
async def update_role(
    role_id: uuid.UUID,
    payload: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles", "write")),
) -> RoleOut:
    role = await role_crud.get(db, role_id, current_user.company_id)
    if role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rol no encontrado")
    if role.is_system:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No se puede modificar un rol de sistema")
    if payload.name and payload.name != role.name:
        existing = await role_crud.get_by_name(db, current_user.company_id, payload.name)
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un rol con ese nombre en la empresa")
    return await role_crud.update(db, role, payload)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles", "delete")),
) -> None:
    role = await role_crud.get(db, role_id, current_user.company_id)
    if role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rol no encontrado")
    if role.is_system:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No se puede eliminar un rol de sistema")
    if await role_crud.has_assigned_users(db, role.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "El rol tiene usuarios asignados")
    await role_crud.delete(db, role)
