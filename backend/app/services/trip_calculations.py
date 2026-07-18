"""Cálculo de nómina de viaje (Fase 2).

Función pura respecto a los datos que recibe (no persiste nada), para que
`GET /trips/{id}/close-preview` y `POST /trips/{id}/close` compartan exactamente
la misma lógica sin duplicarla — el primero solo la muestra, el segundo además
la guarda en `trip_payroll` vía `crud/trip_payroll.py`.

Fórmula aprobada:
    trip_days      = (ended_at.date() - started_at.date()).days + 1   (mínimo 1)
    base_salary    = daily_base_rate × trip_days
    meal_allowance = meal_allowance_per_day × trip_days
    holiday_bonus  = holiday_bonus_rate × (# feriados de la empresa dentro del rango del viaje)
    return_bonus   = return_bonus_rate si trip.is_round_trip, si no 0
    bonuses        = meal_allowance + holiday_bonus + return_bonus
    total_to_pay   = base_salary + bonuses - advance_payment
"""

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import company_holiday as company_holiday_crud
from app.crud import driver_pay_rate as driver_pay_rate_crud
from app.models.trip import Trip


def compute_trip_days(started_at: datetime, ended_at: datetime) -> int:
    days = (ended_at.date() - started_at.date()).days + 1
    return max(days, 1)


async def calculate_payroll_breakdown(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    trip: Trip,
    vehicle_type: str,
    ended_at: datetime,
    advance_payment: float,
) -> dict:
    trip_days = compute_trip_days(trip.started_at, ended_at)
    pay_rate = await driver_pay_rate_crud.get_by_vehicle_type(db, company_id, vehicle_type)

    if pay_rate is None:
        return {
            "trip_days": trip_days,
            "base_salary": 0.0,
            "meal_allowance": 0.0,
            "holiday_bonus": 0.0,
            "holiday_count": 0,
            "return_bonus": 0.0,
            "bonuses": 0.0,
            "advance_payment": advance_payment,
            "total_to_pay": -advance_payment,
            "missing_pay_rate": True,
        }

    holiday_count = await company_holiday_crud.count_between(
        db, company_id, trip.started_at.date(), ended_at.date()
    )
    base_salary = float(pay_rate.daily_base_rate) * trip_days
    meal_allowance = float(pay_rate.meal_allowance_per_day) * trip_days
    holiday_bonus = float(pay_rate.holiday_bonus_rate) * holiday_count
    return_bonus = float(pay_rate.return_bonus_rate) if trip.is_round_trip else 0.0
    bonuses = meal_allowance + holiday_bonus + return_bonus
    total_to_pay = base_salary + bonuses - advance_payment

    return {
        "trip_days": trip_days,
        "base_salary": base_salary,
        "meal_allowance": meal_allowance,
        "holiday_bonus": holiday_bonus,
        "holiday_count": holiday_count,
        "return_bonus": return_bonus,
        "bonuses": bonuses,
        "advance_payment": advance_payment,
        "total_to_pay": total_to_pay,
        "missing_pay_rate": False,
    }
