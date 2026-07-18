import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.vehicle import VEHICLE_TYPES


class DriverPayRateBase(BaseModel):
    vehicle_type: str = Field(pattern="^(" + "|".join(VEHICLE_TYPES) + ")$")
    daily_base_rate: float = Field(ge=0)
    meal_allowance_per_day: float = Field(ge=0, default=0)
    holiday_bonus_rate: float = Field(ge=0, default=0)
    return_bonus_rate: float = Field(ge=0, default=0)


class DriverPayRateCreate(DriverPayRateBase):
    pass


class DriverPayRateUpdate(BaseModel):
    daily_base_rate: float | None = Field(default=None, ge=0)
    meal_allowance_per_day: float | None = Field(default=None, ge=0)
    holiday_bonus_rate: float | None = Field(default=None, ge=0)
    return_bonus_rate: float | None = Field(default=None, ge=0)


class DriverPayRateOut(DriverPayRateBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
