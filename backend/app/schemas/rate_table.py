import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.vehicle import VEHICLE_TYPES


class RateTableBase(BaseModel):
    origin: str = Field(min_length=1, max_length=255)
    destination: str = Field(min_length=1, max_length=255)
    vehicle_type: str = Field(pattern="^(" + "|".join(VEHICLE_TYPES) + ")$")
    cargo_type: str = Field(min_length=1, max_length=100)
    distance_km: float = Field(ge=0)
    freight_amount: float = Field(ge=0)


class RateTableCreate(RateTableBase):
    pass


class RateTableUpdate(BaseModel):
    origin: str | None = Field(default=None, min_length=1, max_length=255)
    destination: str | None = Field(default=None, min_length=1, max_length=255)
    cargo_type: str | None = Field(default=None, min_length=1, max_length=100)
    distance_km: float | None = Field(default=None, ge=0)
    freight_amount: float | None = Field(default=None, ge=0)
    is_active: bool | None = None


class RateTableOut(RateTableBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
