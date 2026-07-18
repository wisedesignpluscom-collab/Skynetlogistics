import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import driver_pay_rate as driver_pay_rate_crud
from app.models.user import User
from app.schemas.driver_pay_rate import DriverPayRateCreate, DriverPayRateOut, DriverPayRateUpdate

router = APIRouter(prefix="/driver-pay-rates", tags=["trip_settings"])


@router.get("", response_model=list[DriverPayRateOut])
async def list_driver_pay_rates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "read")),
) -> list[DriverPayRateOut]:
    return await driver_pay_rate_crud.list_all_for_company(db, current_user.company_id)


@router.post("", response_model=DriverPayRateOut, status_code=status.HTTP_201_CREATED)
async def create_driver_pay_rate(
    payload: DriverPayRateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "write")),
) -> DriverPayRateOut:
    existing = await driver_pay_rate_crud.get_by_vehicle_type(
        db, current_user.company_id, payload.vehicle_type
    )
    if existing is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Ya existe un tabulado de pago para ese tipo de vehículo"
        )
    return await driver_pay_rate_crud.create(db, current_user.company_id, payload)


@router.patch("/{rate_id}", response_model=DriverPayRateOut)
async def update_driver_pay_rate(
    rate_id: uuid.UUID,
    payload: DriverPayRateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "write")),
) -> DriverPayRateOut:
    rate = await driver_pay_rate_crud.get(db, rate_id, current_user.company_id)
    if rate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tabulado de pago no encontrado")
    return await driver_pay_rate_crud.update(db, rate, payload)


@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver_pay_rate(
    rate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "delete")),
) -> None:
    rate = await driver_pay_rate_crud.get(db, rate_id, current_user.company_id)
    if rate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tabulado de pago no encontrado")
    await driver_pay_rate_crud.delete(db, rate)
