import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import driver as driver_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.driver import DriverCreate, DriverOut, DriverUpdate

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("", response_model=Page[DriverOut])
async def list_drivers(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "read")),
) -> Page[DriverOut]:
    items, total = await driver_crud.list_paginated(
        db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        search=search,
        status=status_filter,
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=DriverOut, status_code=status.HTTP_201_CREATED)
async def create_driver(
    payload: DriverCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "write")),
) -> DriverOut:
    if await driver_crud.get_by_license(db, current_user.company_id, payload.license_number) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un conductor con ese número de licencia")
    return await driver_crud.create(db, current_user.company_id, payload)


@router.get("/{driver_id}", response_model=DriverOut)
async def get_driver(
    driver_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "read")),
) -> DriverOut:
    driver = await driver_crud.get(db, driver_id, current_user.company_id)
    if driver is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conductor no encontrado")
    return driver


@router.patch("/{driver_id}", response_model=DriverOut)
async def update_driver(
    driver_id: uuid.UUID,
    payload: DriverUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "write")),
) -> DriverOut:
    driver = await driver_crud.get(db, driver_id, current_user.company_id)
    if driver is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conductor no encontrado")
    if payload.license_number and payload.license_number != driver.license_number:
        existing = await driver_crud.get_by_license(db, current_user.company_id, payload.license_number)
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un conductor con ese número de licencia")
    return await driver_crud.update(db, driver, payload)


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver(
    driver_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "delete")),
) -> None:
    driver = await driver_crud.get(db, driver_id, current_user.company_id)
    if driver is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conductor no encontrado")
    await driver_crud.deactivate(db, driver)
