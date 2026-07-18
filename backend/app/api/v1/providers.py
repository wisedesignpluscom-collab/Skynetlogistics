import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import provider as provider_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.provider import ProviderCreate, ProviderOut, ProviderUpdate

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("", response_model=Page[ProviderOut])
async def list_providers(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("providers", "read")),
) -> Page[ProviderOut]:
    items, total = await provider_crud.list_paginated(
        db, company_id=current_user.company_id, page=page, page_size=page_size
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=ProviderOut, status_code=status.HTTP_201_CREATED)
async def create_provider(
    payload: ProviderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("providers", "write")),
) -> ProviderOut:
    return await provider_crud.create(db, current_user.company_id, payload)


@router.get("/{provider_id}", response_model=ProviderOut)
async def get_provider(
    provider_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("providers", "read")),
) -> ProviderOut:
    provider = await provider_crud.get(db, provider_id, current_user.company_id)
    if provider is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Proveedor no encontrado")
    return provider


@router.patch("/{provider_id}", response_model=ProviderOut)
async def update_provider(
    provider_id: uuid.UUID,
    payload: ProviderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("providers", "write")),
) -> ProviderOut:
    provider = await provider_crud.get(db, provider_id, current_user.company_id)
    if provider is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Proveedor no encontrado")
    return await provider_crud.update(db, provider, payload)


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("providers", "delete")),
) -> None:
    provider = await provider_crud.get(db, provider_id, current_user.company_id)
    if provider is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Proveedor no encontrado")
    await provider_crud.delete(db, provider)
