import uuid
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.custom_fields import validate_entity_custom_data
from app.core.deps import require_permission
from app.crud import tire as tire_crud
from app.crud import tire_movement as tire_movement_crud
from app.crud import vehicle as vehicle_crud
from app.jobs.alerts import run_alert_checks
from app.models.user import User
from app.schemas.common import Page
from app.schemas.tire import TireCreate, TireDetailOut, TireOut, TirePerformanceRow, TireUpdate
from app.services.tire_km import calculate_tire_km, compute_performance
from app.services.workflows import run_workflows

router = APIRouter(prefix="/tires", tags=["tires"])


@router.get("", response_model=Page[TireOut])
async def list_tires(
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = None,
    brand: str | None = None,
    model: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "read")),
) -> Page[TireOut]:
    items, total = await tire_crud.list_paginated(
        db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        status=status_filter,
        brand=brand,
        model=model,
        search=search,
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=TireOut, status_code=status.HTTP_201_CREATED)
async def create_tire(
    payload: TireCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "write")),
) -> TireOut:
    if await tire_crud.get_by_unique_code(db, current_user.company_id, payload.unique_code) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un neumático con ese código")
    payload.custom_data = await validate_entity_custom_data(
        db, current_user.company_id, "tire", payload.custom_data, payload=payload
    )
    tire = await tire_crud.create(db, current_user.company_id, payload)
    await run_workflows(db, company_id=current_user.company_id, entity_type="tire", event="creado", entity=tire)
    return tire


@router.get("/analytics/performance", response_model=list[TirePerformanceRow])
async def get_tire_performance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "read")),
) -> list[TirePerformanceRow]:
    tires = await tire_crud.list_all_for_company(db, current_user.company_id)
    movements = await tire_movement_crud.list_all_for_company(db, current_user.company_id)
    performance = compute_performance(tires, movements)
    return [TirePerformanceRow(**asdict(row)) for row in performance]


@router.get("/{tire_id}", response_model=TireDetailOut)
async def get_tire(
    tire_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "read")),
) -> TireDetailOut:
    tire = await tire_crud.get(db, tire_id, current_user.company_id)
    if tire is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Neumático no encontrado")

    movements = await tire_movement_crud.list_for_tire(db, tire_id, current_user.company_id)

    current_odometer_km: int | None = None
    if tire.status == "instalado" and tire.vehicle_id is not None:
        vehicle = await vehicle_crud.get(db, tire.vehicle_id, current_user.company_id)
        if vehicle is not None:
            current_odometer_km = vehicle.current_odometer_km

    km_current_period, km_lifetime_total = calculate_tire_km(movements, current_odometer_km)

    return TireDetailOut(
        **TireOut.model_validate(tire).model_dump(),
        movements=list(reversed(movements)),
        km_current_period=km_current_period,
        km_lifetime_total=km_lifetime_total,
    )


@router.patch("/{tire_id}", response_model=TireOut)
async def update_tire(
    tire_id: uuid.UUID,
    payload: TireUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "write")),
) -> TireOut:
    tire = await tire_crud.get(db, tire_id, current_user.company_id)
    if tire is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Neumático no encontrado")
    if payload.custom_data is not None:
        payload.custom_data = await validate_entity_custom_data(
            db, current_user.company_id, "tire", payload.custom_data, payload=payload
        )
    updated = await tire_crud.update(db, tire, payload)
    if payload.current_thickness_mm is not None and updated.status == "instalado" and updated.vehicle_id:
        await run_alert_checks(db, vehicle_ids=[updated.vehicle_id])
    await run_workflows(db, company_id=current_user.company_id, entity_type="tire", event="actualizado", entity=updated)
    return updated
