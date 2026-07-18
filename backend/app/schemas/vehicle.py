import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.vehicle import VEHICLE_STATUSES, VEHICLE_TYPES


class VehicleBase(BaseModel):
    plate: str = Field(min_length=1, max_length=20)
    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1950, le=2100)
    vin: str | None = Field(default=None, max_length=50)
    type: str = Field(pattern="^(" + "|".join(VEHICLE_TYPES) + ")$")
    assigned_driver_id: uuid.UUID | None = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    plate: str | None = Field(default=None, min_length=1, max_length=20)
    brand: str | None = Field(default=None, min_length=1, max_length=100)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=1950, le=2100)
    vin: str | None = Field(default=None, max_length=50)
    status: str | None = Field(default=None, pattern="^(" + "|".join(VEHICLE_STATUSES) + ")$")
    current_odometer_km: int | None = Field(default=None, ge=0)
    assigned_driver_id: uuid.UUID | None = None


class VehicleOut(VehicleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    status: str
    current_odometer_km: int
    created_at: datetime
    updated_at: datetime
