import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TripPayrollOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trip_id: uuid.UUID
    base_salary: float
    meal_allowance: float
    holiday_bonus: float
    return_bonus: float
    bonuses: float
    advance_payment: float
    total_to_pay: float
    created_at: datetime
    updated_at: datetime


class TripClosePreview(BaseModel):
    """Desglose calculado sin persistir — usado por la vista de cierre de viaje."""

    trip_days: int
    base_salary: float
    meal_allowance: float
    holiday_bonus: float
    holiday_count: int
    return_bonus: float
    bonuses: float
    advance_payment: float
    total_to_pay: float
    freight_cost: float | None
    missing_pay_rate: bool = False
