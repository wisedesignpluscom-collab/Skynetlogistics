import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.core.security import verify_password
from app.crud import role as role_crud
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.user import UserCreate, UserPasswordUpdate, UserUpdate, UserWithRoleOut
from app.utils.permissions import has_permission

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=Page[UserWithRoleOut])
async def list_users(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    role_id: uuid.UUID | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users", "read")),
) -> Page[UserWithRoleOut]:
    items, total = await user_crud.list_paginated(
        db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        search=search,
        role_id=role_id,
        is_active=is_active,
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=UserWithRoleOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users", "write")),
) -> UserWithRoleOut:
    role = await role_crud.get(db, payload.role_id, current_user.company_id)
    if role is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El rol no pertenece a esta empresa")
    if await user_crud.get_by_email(db, payload.email) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un usuario con ese email")
    return await user_crud.create(db, current_user.company_id, payload)


@router.get("/{user_id}", response_model=UserWithRoleOut)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users", "read")),
) -> UserWithRoleOut:
    user = await user_crud.get(db, user_id, current_user.company_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return user


@router.patch("/{user_id}", response_model=UserWithRoleOut)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users", "write")),
) -> UserWithRoleOut:
    user = await user_crud.get(db, user_id, current_user.company_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    if payload.role_id and payload.role_id != user.role_id:
        role = await role_crud.get(db, payload.role_id, current_user.company_id)
        if role is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "El rol no pertenece a esta empresa")
    return await user_crud.update(db, user, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users", "delete")),
) -> None:
    if user_id == current_user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No puedes desactivar tu propio usuario")
    user = await user_crud.get(db, user_id, current_user.company_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    await user_crud.deactivate(db, user)


@router.patch("/{user_id}/password", response_model=UserWithRoleOut)
async def update_password(
    user_id: uuid.UUID,
    payload: UserPasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserWithRoleOut:
    is_self = user_id == current_user.id
    if not is_self and not current_user.is_superadmin:
        if not has_permission(current_user.role.permissions, "users", "write"):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso para esta acción")

    user = await user_crud.get(db, user_id, current_user.company_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")

    if is_self:
        if not payload.current_password or not verify_password(
            payload.current_password, user.password_hash
        ):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Password actual incorrecto")

    return await user_crud.set_password(db, user, payload.new_password)
