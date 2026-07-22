import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import vrp_run as vrp_run_crud
from app.models.user import User
from app.schemas.vehicle import VehicleOut
from app.schemas.vrp import VrpOptimizeRequest, VrpRunOut
from app.services.vrp_planning import confirm_run, get_available_vehicles, propose_optimization

router = APIRouter(prefix="/vrp", tags=["vrp"])


@router.get("/available-vehicles", response_model=list[VehicleOut])
async def list_available_vehicles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "read")),
) -> list[VehicleOut]:
    return await get_available_vehicles(db, current_user.company_id)


@router.post("/optimize", response_model=VrpRunOut, status_code=status.HTTP_201_CREATED)
async def optimize(
    payload: VrpOptimizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> VrpRunOut:
    try:
        run = await propose_optimization(
            db,
            company_id=current_user.company_id,
            created_by=current_user.id,
            stops=[s.model_dump() for s in payload.stops] if payload.stops else None,
            order_ids=payload.order_ids,
            cargo_type=payload.cargo_type,
            vehicle_ids=payload.vehicle_ids,
            enforce_capacity=payload.enforce_capacity,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return run


@router.get("/runs/{run_id}", response_model=VrpRunOut)
async def get_run(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "read")),
) -> VrpRunOut:
    run = await vrp_run_crud.get(db, run_id, current_user.company_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Corrida de optimización no encontrada")
    return run


@router.post("/runs/{run_id}/confirm", response_model=VrpRunOut)
async def confirm(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> VrpRunOut:
    run = await vrp_run_crud.get(db, run_id, current_user.company_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Corrida de optimización no encontrada")
    try:
        await confirm_run(db, run)
    except ValueError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    return await vrp_run_crud.get(db, run_id, current_user.company_id)


@router.post("/runs/{run_id}/discard", response_model=VrpRunOut)
async def discard(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> VrpRunOut:
    run = await vrp_run_crud.get(db, run_id, current_user.company_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Corrida de optimización no encontrada")
    if run.status != "propuesto":
        raise HTTPException(status.HTTP_409_CONFLICT, "Esta corrida ya fue confirmada o descartada")
    return await vrp_run_crud.mark_discarded(db, run)
