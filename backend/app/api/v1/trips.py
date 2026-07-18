import uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import driver as driver_crud
from app.crud import rate_table as rate_table_crud
from app.crud import trip as trip_crud
from app.crud import trip_expense as trip_expense_crud
from app.crud import trip_payroll as trip_payroll_crud
from app.crud import vehicle as vehicle_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.trip import (
    TripAdvance,
    TripClose,
    TripCreate,
    TripOut,
    TripStart,
    TripUpdate,
    TripWithDetailsOut,
)
from app.schemas.trip_expense import TripExpenseCreate, TripExpenseOut
from app.schemas.trip_payroll import TripClosePreview
from app.services.trip_calculations import calculate_payroll_breakdown
from app.services.vehicle_odometer import advance_odometer

router = APIRouter(prefix="/trips", tags=["trips"])


async def _get_trip_or_404(db: AsyncSession, trip_id: uuid.UUID, company_id: uuid.UUID):
    trip = await trip_crud.get(db, trip_id, company_id)
    if trip is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Viaje no encontrado")
    return trip


@router.get("", response_model=Page[TripOut])
async def list_trips(
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = None,
    driver_id: uuid.UUID | None = None,
    vehicle_id: uuid.UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "read")),
) -> Page[TripOut]:
    items, total = await trip_crud.list_paginated(
        db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        status=status_filter,
        driver_id=driver_id,
        vehicle_id=vehicle_id,
        date_from=date_from,
        date_to=date_to,
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=TripOut, status_code=status.HTTP_201_CREATED)
async def create_trip(
    payload: TripCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> TripOut:
    vehicle = await vehicle_crud.get(db, payload.vehicle_id, current_user.company_id)
    if vehicle is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El vehículo no pertenece a esta empresa")
    if await driver_crud.get(db, payload.driver_id, current_user.company_id) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El conductor no pertenece a esta empresa")

    if payload.trailer_id is not None:
        trailer = await vehicle_crud.get(db, payload.trailer_id, current_user.company_id)
        if trailer is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "El remolque no pertenece a esta empresa")
        if trailer.type != "remolque":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "trailer_id debe ser un vehículo tipo remolque")

    rate_match = await rate_table_crud.find_match(
        db,
        company_id=current_user.company_id,
        origin=payload.origin,
        destination=payload.destination,
        vehicle_type=vehicle.type,
        cargo_type=payload.cargo_type,
    )
    distance_km = float(rate_match.distance_km) if rate_match else None
    freight_cost = float(rate_match.freight_amount) if rate_match else None

    return await trip_crud.create(
        db, current_user.company_id, payload, distance_km=distance_km, freight_cost=freight_cost
    )


@router.get("/{trip_id}", response_model=TripWithDetailsOut)
async def get_trip(
    trip_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "read")),
) -> TripWithDetailsOut:
    trip = await trip_crud.get_with_details(db, trip_id, current_user.company_id)
    if trip is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Viaje no encontrado")
    return trip


@router.patch("/{trip_id}", response_model=TripOut)
async def update_trip(
    trip_id: uuid.UUID,
    payload: TripUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> TripOut:
    trip = await _get_trip_or_404(db, trip_id, current_user.company_id)
    if trip.status != "planificado":
        raise HTTPException(status.HTTP_409_CONFLICT, "Solo se puede editar un viaje planificado")
    return await trip_crud.update(db, trip, payload)


@router.post("/{trip_id}/start", response_model=TripOut)
async def start_trip(
    trip_id: uuid.UUID,
    payload: TripStart,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> TripOut:
    trip = await _get_trip_or_404(db, trip_id, current_user.company_id)
    if trip.status != "planificado":
        raise HTTPException(status.HTTP_409_CONFLICT, "El viaje ya fue iniciado")
    vehicle = await vehicle_crud.get(db, trip.vehicle_id, current_user.company_id)
    if payload.start_odometer_km < vehicle.current_odometer_km:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"El odómetro de inicio no puede ser menor al actual del vehículo ({vehicle.current_odometer_km} km)",
        )
    return await trip_crud.start(db, trip, payload.start_odometer_km)


@router.patch("/{trip_id}/advance", response_model=TripOut)
async def set_trip_advance(
    trip_id: uuid.UUID,
    payload: TripAdvance,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> TripOut:
    trip = await _get_trip_or_404(db, trip_id, current_user.company_id)
    if trip.status not in ("planificado", "en_curso"):
        raise HTTPException(status.HTTP_409_CONFLICT, "No se puede registrar un anticipo en este estado")
    return await trip_crud.set_advance_payment(db, trip, payload.advance_payment)


@router.get("/{trip_id}/expenses", response_model=list[TripExpenseOut])
async def list_trip_expenses(
    trip_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "read")),
) -> list[TripExpenseOut]:
    await _get_trip_or_404(db, trip_id, current_user.company_id)
    return await trip_expense_crud.list_for_trip(db, trip_id)


@router.post("/{trip_id}/expenses", response_model=TripExpenseOut, status_code=status.HTTP_201_CREATED)
async def create_trip_expense(
    trip_id: uuid.UUID,
    payload: TripExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> TripExpenseOut:
    trip = await _get_trip_or_404(db, trip_id, current_user.company_id)
    if trip.status != "en_curso":
        raise HTTPException(status.HTTP_409_CONFLICT, "Solo se registran gastos en un viaje en curso")
    return await trip_expense_crud.create(db, trip_id, payload, recorded_by=current_user.id)


@router.delete("/{trip_id}/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip_expense(
    trip_id: uuid.UUID,
    expense_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "delete")),
) -> None:
    await _get_trip_or_404(db, trip_id, current_user.company_id)
    expense = await trip_expense_crud.get(db, expense_id, trip_id)
    if expense is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Gasto no encontrado")
    await trip_expense_crud.delete(db, expense)


@router.get("/{trip_id}/close-preview", response_model=TripClosePreview)
async def close_trip_preview(
    trip_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "read")),
) -> TripClosePreview:
    trip = await _get_trip_or_404(db, trip_id, current_user.company_id)
    if trip.status != "en_curso":
        raise HTTPException(status.HTTP_409_CONFLICT, "El viaje debe estar en curso para previsualizar el cierre")
    vehicle = await vehicle_crud.get(db, trip.vehicle_id, current_user.company_id)
    breakdown = await calculate_payroll_breakdown(
        db,
        company_id=current_user.company_id,
        trip=trip,
        vehicle_type=vehicle.type,
        ended_at=datetime.now(timezone.utc),
        advance_payment=float(trip.advance_payment),
    )
    return TripClosePreview(freight_cost=trip.freight_cost, **breakdown)


@router.post("/{trip_id}/close", response_model=TripWithDetailsOut)
async def close_trip(
    trip_id: uuid.UUID,
    payload: TripClose,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> TripWithDetailsOut:
    trip = await _get_trip_or_404(db, trip_id, current_user.company_id)
    if trip.status != "en_curso":
        raise HTTPException(status.HTTP_409_CONFLICT, "El viaje debe estar en curso para cerrarlo")
    if payload.end_odometer_km < trip.start_odometer_km:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "El odómetro final no puede ser menor al odómetro de inicio"
        )

    vehicle = await vehicle_crud.get(db, trip.vehicle_id, current_user.company_id)
    advance_payment = (
        payload.advance_payment if payload.advance_payment is not None else float(trip.advance_payment)
    )
    ended_at = datetime.now(timezone.utc)
    breakdown = await calculate_payroll_breakdown(
        db,
        company_id=current_user.company_id,
        trip=trip,
        vehicle_type=vehicle.type,
        ended_at=ended_at,
        advance_payment=advance_payment,
    )
    if breakdown["missing_pay_rate"]:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"No hay tabulado de pago configurado para el tipo de vehículo '{vehicle.type}'",
        )

    if payload.advance_payment is not None:
        await trip_crud.set_advance_payment(db, trip, payload.advance_payment)

    await trip_payroll_crud.create(
        db,
        trip.id,
        base_salary=breakdown["base_salary"],
        meal_allowance=breakdown["meal_allowance"],
        holiday_bonus=breakdown["holiday_bonus"],
        return_bonus=breakdown["return_bonus"],
        advance_payment=advance_payment,
    )
    await trip_crud.close(
        db, trip, end_odometer_km=payload.end_odometer_km, freight_cost=payload.freight_cost
    )
    await advance_odometer(db, vehicle, payload.end_odometer_km)

    return await trip_crud.get_with_details(db, trip.id, current_user.company_id)


@router.post("/{trip_id}/cancel", response_model=TripOut)
async def cancel_trip(
    trip_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trips", "write")),
) -> TripOut:
    trip = await _get_trip_or_404(db, trip_id, current_user.company_id)
    if trip.status not in ("planificado", "en_curso"):
        raise HTTPException(status.HTTP_409_CONFLICT, "El viaje no se puede cancelar en este estado")
    return await trip_crud.cancel(db, trip)
