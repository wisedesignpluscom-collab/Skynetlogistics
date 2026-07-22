import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import driver as driver_crud
from app.crud import driver_document as driver_document_crud
from app.crud import user as user_crud
from app.jobs.alerts import run_alert_checks
from app.models.user import User
from app.schemas.common import Page
from app.schemas.driver import DriverCreate, DriverOut, DriverUpdate
from app.schemas.driver_document import DriverDocumentCreate, DriverDocumentOut
from app.services.custom_fields import validate_entity_custom_data
from app.services.workflows import run_workflows

router = APIRouter(prefix="/drivers", tags=["drivers"])


async def _validate_user_link(db: AsyncSession, company_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """Valida que `user_id` sea un usuario de la misma empresa y que no esté ya vinculado a otro
    conductor — mismo criterio de validación cross-tenant que warehouse_id/vehicle_id en
    inventory_items (Fase 6)."""
    user = await user_crud.get(db, user_id, company_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    existing = await driver_crud.get_by_user_id(db, user_id)
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ese usuario ya está vinculado a otro conductor")


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
    if payload.user_id is not None:
        await _validate_user_link(db, current_user.company_id, payload.user_id)
    payload.custom_data = await validate_entity_custom_data(
        db, current_user.company_id, "driver", payload.custom_data, payload=payload
    )
    driver = await driver_crud.create(db, current_user.company_id, payload)
    await run_workflows(db, company_id=current_user.company_id, entity_type="driver", event="creado", entity=driver)
    return driver


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
    if payload.user_id is not None and payload.user_id != driver.user_id:
        await _validate_user_link(db, current_user.company_id, payload.user_id)
    if payload.custom_data is not None:
        payload.custom_data = await validate_entity_custom_data(
            db, current_user.company_id, "driver", payload.custom_data, payload=payload
        )
    previous_status = driver.status
    updated = await driver_crud.update(db, driver, payload)
    await run_workflows(db, company_id=current_user.company_id, entity_type="driver", event="actualizado", entity=updated)
    if payload.status is not None and payload.status != previous_status:
        await run_workflows(
            db, company_id=current_user.company_id, entity_type="driver", event="cambio_estado",
            entity=updated, previous_status=previous_status,
        )
    return updated


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


@router.get("/{driver_id}/documents", response_model=list[DriverDocumentOut])
async def list_driver_documents(
    driver_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "read")),
) -> list[DriverDocumentOut]:
    driver = await driver_crud.get(db, driver_id, current_user.company_id)
    if driver is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conductor no encontrado")
    return await driver_document_crud.list_for_driver(db, driver_id, current_user.company_id)


@router.post(
    "/{driver_id}/documents", response_model=DriverDocumentOut, status_code=status.HTTP_201_CREATED
)
async def create_driver_document(
    driver_id: uuid.UUID,
    payload: DriverDocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "write")),
) -> DriverDocumentOut:
    driver = await driver_crud.get(db, driver_id, current_user.company_id)
    if driver is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conductor no encontrado")
    document = await driver_document_crud.create(db, current_user.company_id, driver_id, payload)
    if payload.expiry_date is not None:
        await run_alert_checks(db, driver_ids=[driver_id])
    return document
