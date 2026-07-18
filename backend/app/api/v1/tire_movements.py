import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import tire as tire_crud
from app.crud import tire_movement as tire_movement_crud
from app.models.user import User
from app.schemas.tire import TireMovementBatchCreate, TireMovementCreate, TireMovementOut
from app.services.tire_movements import InvalidTireMovement, apply_movement

router = APIRouter(prefix="/tire-movements", tags=["tires"])


@router.get("", response_model=list[TireMovementOut])
async def list_tire_movements(
    tire_id: uuid.UUID | None = None,
    vehicle_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "read")),
) -> list[TireMovementOut]:
    return await tire_movement_crud.list_filtered(
        db, company_id=current_user.company_id, tire_id=tire_id, vehicle_id=vehicle_id
    )


@router.post("", response_model=TireMovementOut, status_code=status.HTTP_201_CREATED)
async def create_tire_movement(
    payload: TireMovementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "write")),
) -> TireMovementOut:
    tire = await tire_crud.get(db, payload.tire_id, current_user.company_id)
    if tire is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Neumático no encontrado")

    try:
        return await apply_movement(
            db,
            tire,
            movement_type=payload.movement_type,
            vehicle_id=payload.vehicle_id,
            axle_number=payload.axle_number,
            axle_side=payload.axle_side,
            axle_dual_position=payload.axle_dual_position,
            warehouse_id=payload.warehouse_id,
            provider_id=payload.provider_id,
            thickness_mm=payload.thickness_mm,
            notes=payload.notes,
            recorded_by=current_user.id,
        )
    except InvalidTireMovement as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


@router.post("/batch", response_model=list[TireMovementOut], status_code=status.HTTP_201_CREATED)
async def create_tire_movement_batch(
    payload: TireMovementBatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "write")),
) -> list[TireMovementOut]:
    results: list[TireMovementOut] = []
    for item in payload.items:
        tire = await tire_crud.get(db, item.tire_id, current_user.company_id)
        if tire is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Neumático {item.tire_id} no encontrado")
        try:
            movement = await apply_movement(
                db,
                tire,
                movement_type=payload.movement_type,
                vehicle_id=payload.vehicle_id,
                axle_number=item.axle_number,
                axle_side=item.axle_side,
                axle_dual_position=item.axle_dual_position,
                warehouse_id=payload.warehouse_id,
                provider_id=payload.provider_id,
                thickness_mm=item.thickness_mm,
                notes=payload.notes,
                recorded_by=current_user.id,
            )
        except InvalidTireMovement as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"{item.tire_id}: {exc}") from exc
        results.append(movement)
    return results
