import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import route_plan as route_plan_crud
from app.crud import route_settings as route_settings_crud
from app.crud import trip as trip_crud
from app.models.user import User
from app.schemas.route import (
    RouteComputeRequest,
    RoutePlanDetailOut,
    RoutePlanOut,
    RouteRecalculationOut,
    RouteSettingsOut,
    RouteSettingsUpdate,
)
from app.services.route_planning import compute_route_plan, recalculate_route

router = APIRouter(tags=["routing"])


async def _plan_detail(db: AsyncSession, plan) -> RoutePlanDetailOut:
    recalcs = await route_plan_crud.list_recalculations(db, plan.id)
    return RoutePlanDetailOut(
        **RoutePlanOut.model_validate(plan).model_dump(),
        recalculations=[RouteRecalculationOut.model_validate(r) for r in recalcs],
    )


# --- Configuración por empresa (mismo patrón que fatigue-rules / tire-settings) ---


@router.get("/route-settings", response_model=RouteSettingsOut)
async def get_route_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "read")),
) -> RouteSettingsOut:
    return await route_settings_crud.get_or_create(db, current_user.company_id)


@router.patch("/route-settings", response_model=RouteSettingsOut)
async def update_route_settings(
    payload: RouteSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> RouteSettingsOut:
    settings = await route_settings_crud.get_or_create(db, current_user.company_id)
    return await route_settings_crud.update(db, settings, payload)


# --- Ruta por viaje ---


@router.post("/trips/{trip_id}/route", response_model=RoutePlanDetailOut)
async def compute_trip_route(
    trip_id: uuid.UUID,
    payload: RouteComputeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> RoutePlanDetailOut:
    if await trip_crud.get(db, trip_id, current_user.company_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Viaje no encontrado")
    plan = await compute_route_plan(
        db,
        company_id=current_user.company_id,
        trip_id=trip_id,
        origin_lat=payload.origin_lat,
        origin_lng=payload.origin_lng,
        destination_lat=payload.destination_lat,
        destination_lng=payload.destination_lng,
    )
    return await _plan_detail(db, plan)


@router.get("/trips/{trip_id}/route", response_model=RoutePlanDetailOut)
async def get_trip_route(
    trip_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "read")),
) -> RoutePlanDetailOut:
    plan = await route_plan_crud.get_by_trip(db, trip_id, current_user.company_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Este viaje no tiene ruta planeada")
    return await _plan_detail(db, plan)


@router.post("/trips/{trip_id}/route/recalculate", response_model=RoutePlanDetailOut)
async def recalculate_trip_route(
    trip_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> RoutePlanDetailOut:
    plan = await route_plan_crud.get_by_trip(db, trip_id, current_user.company_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Este viaje no tiene ruta planeada")
    await recalculate_route(db, plan, reason="manual")
    plan = await route_plan_crud.get_by_trip(db, trip_id, current_user.company_id)
    return await _plan_detail(db, plan)
