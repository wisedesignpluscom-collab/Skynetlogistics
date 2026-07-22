import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.custom_fields import validate_entity_custom_data
from app.core.deps import require_permission
from app.crud import client as client_crud
from app.models.user import User
from app.schemas.client import ClientCreate, ClientOut, ClientUpdate
from app.schemas.common import Page
from app.services.workflows import run_workflows

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=Page[ClientOut])
async def list_clients(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "read")),
) -> Page[ClientOut]:
    items, total = await client_crud.list_paginated(
        db, company_id=current_user.company_id, page=page, page_size=page_size, search=search
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> ClientOut:
    payload.custom_data = await validate_entity_custom_data(
        db, current_user.company_id, "client", payload.custom_data, payload=payload
    )
    client = await client_crud.create(db, current_user.company_id, payload)
    await run_workflows(db, company_id=current_user.company_id, entity_type="client", event="creado", entity=client)
    return client


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "read")),
) -> ClientOut:
    client = await client_crud.get(db, client_id, current_user.company_id)
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
    return client


@router.patch("/{client_id}", response_model=ClientOut)
async def update_client(
    client_id: uuid.UUID,
    payload: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> ClientOut:
    client = await client_crud.get(db, client_id, current_user.company_id)
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
    if payload.custom_data is not None:
        payload.custom_data = await validate_entity_custom_data(
            db, current_user.company_id, "client", payload.custom_data, payload=payload
        )
    updated = await client_crud.update(db, client, payload)
    await run_workflows(db, company_id=current_user.company_id, entity_type="client", event="actualizado", entity=updated)
    return updated


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "delete")),
) -> None:
    client = await client_crud.get(db, client_id, current_user.company_id)
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
    await client_crud.deactivate(db, client)
