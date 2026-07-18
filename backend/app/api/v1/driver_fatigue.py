import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import driver as driver_crud
from app.crud import driver_fatigue_log as fatigue_log_crud
from app.models.user import User
from app.schemas.driver_fatigue_log import DriverFatigueLogOut, DriverFatigueSummaryOut

router = APIRouter(tags=["fatigue"])


@router.get("/drivers/fatigue-summary", response_model=list[DriverFatigueSummaryOut])
async def get_drivers_fatigue_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("fatigue", "read")),
) -> list[DriverFatigueSummaryOut]:
    drivers = await driver_crud.list_all_for_company(db, current_user.company_id)
    latest_by_driver = await fatigue_log_crud.get_latest_for_drivers(db, [d.id for d in drivers])

    summaries: list[DriverFatigueSummaryOut] = []
    for driver in drivers:
        log = latest_by_driver.get(driver.id)
        summaries.append(
            DriverFatigueSummaryOut(
                driver_id=driver.id,
                risk_level=log.risk_level if log else None,
                risk_score=log.risk_score if log else None,
                computed_at=log.computed_at if log else None,
            )
        )
    return summaries


@router.get("/drivers/{driver_id}/fatigue-status", response_model=DriverFatigueLogOut | None)
async def get_driver_fatigue_status(
    driver_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("fatigue", "read")),
) -> DriverFatigueLogOut | None:
    if await driver_crud.get(db, driver_id, current_user.company_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conductor no encontrado")
    return await fatigue_log_crud.get_latest_for_driver(db, driver_id)


@router.get("/drivers/{driver_id}/fatigue-history", response_model=list[DriverFatigueLogOut])
async def get_driver_fatigue_history(
    driver_id: uuid.UUID,
    date_from: date,
    date_to: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("fatigue", "read")),
) -> list[DriverFatigueLogOut]:
    if await driver_crud.get(db, driver_id, current_user.company_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conductor no encontrado")
    return await fatigue_log_crud.list_history(db, driver_id, date_from=date_from, date_to=date_to)
