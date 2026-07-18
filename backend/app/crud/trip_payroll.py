import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip_payroll import TripPayroll


async def create(
    db: AsyncSession,
    trip_id: uuid.UUID,
    *,
    base_salary: float,
    meal_allowance: float,
    holiday_bonus: float,
    return_bonus: float,
    advance_payment: float,
) -> TripPayroll:
    bonuses = meal_allowance + holiday_bonus + return_bonus
    total_to_pay = base_salary + bonuses - advance_payment
    payroll = TripPayroll(
        trip_id=trip_id,
        base_salary=base_salary,
        meal_allowance=meal_allowance,
        holiday_bonus=holiday_bonus,
        return_bonus=return_bonus,
        bonuses=bonuses,
        advance_payment=advance_payment,
        total_to_pay=total_to_pay,
    )
    db.add(payroll)
    await db.commit()
    await db.refresh(payroll)
    return payroll
