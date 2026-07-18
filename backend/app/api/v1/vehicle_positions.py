import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import vehicle as vehicle_crud
from app.crud import vehicle_position as vehicle_position_crud
from app.models.user import User
from app.schemas.vehicle_position import VehiclePositionOut

router = APIRouter(tags=["gps"])


@router.get("/vehicles/{vehicle_id}/position/latest", response_model=VehiclePositionOut | None)
async def get_latest_position(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("gps", "read")),
) -> VehiclePositionOut | None:
    if await vehicle_crud.get(db, vehicle_id, current_user.company_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
    return await vehicle_position_crud.get_latest_for_vehicle(db, vehicle_id, current_user.company_id)


@router.get("/vehicles/{vehicle_id}/positions", response_model=list[VehiclePositionOut])
async def get_position_history(
    vehicle_id: uuid.UUID,
    date_from: datetime,
    date_to: datetime,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("gps", "read")),
) -> list[VehiclePositionOut]:
    if await vehicle_crud.get(db, vehicle_id, current_user.company_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
    return await vehicle_position_crud.list_history(
        db, vehicle_id=vehicle_id, company_id=current_user.company_id, date_from=date_from, date_to=date_to
    )


@router.get("/fleet/positions/latest", response_model=list[VehiclePositionOut])
async def get_fleet_latest_positions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("gps", "read")),
) -> list[VehiclePositionOut]:
    return await vehicle_position_crud.get_latest_for_fleet(db, current_user.company_id)
