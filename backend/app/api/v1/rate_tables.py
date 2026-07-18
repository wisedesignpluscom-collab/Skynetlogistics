import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import rate_table as rate_table_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.rate_table import RateTableCreate, RateTableOut, RateTableUpdate

router = APIRouter(prefix="/rate-tables", tags=["trip_settings"])


@router.get("", response_model=Page[RateTableOut])
async def list_rate_tables(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "read")),
) -> Page[RateTableOut]:
    items, total = await rate_table_crud.list_paginated(
        db, company_id=current_user.company_id, page=page, page_size=page_size
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=RateTableOut, status_code=status.HTTP_201_CREATED)
async def create_rate_table(
    payload: RateTableCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "write")),
) -> RateTableOut:
    existing = await rate_table_crud.find_match(
        db,
        company_id=current_user.company_id,
        origin=payload.origin,
        destination=payload.destination,
        vehicle_type=payload.vehicle_type,
        cargo_type=payload.cargo_type,
    )
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un tabulado para esa ruta/unidad/carga")
    return await rate_table_crud.create(db, current_user.company_id, payload)


@router.patch("/{rate_table_id}", response_model=RateTableOut)
async def update_rate_table(
    rate_table_id: uuid.UUID,
    payload: RateTableUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "write")),
) -> RateTableOut:
    rate_table = await rate_table_crud.get(db, rate_table_id, current_user.company_id)
    if rate_table is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tabulado no encontrado")
    return await rate_table_crud.update(db, rate_table, payload)


@router.delete("/{rate_table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rate_table(
    rate_table_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "delete")),
) -> None:
    rate_table = await rate_table_crud.get(db, rate_table_id, current_user.company_id)
    if rate_table is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tabulado no encontrado")
    await rate_table_crud.delete(db, rate_table)
