import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.trip_expense import TripExpenseOut
from app.schemas.trip_payroll import TripPayrollOut


class TripCreate(BaseModel):
    vehicle_id: uuid.UUID
    driver_id: uuid.UUID
    trailer_id: uuid.UUID | None = None
    origin: str = Field(min_length=1, max_length=255)
    destination: str = Field(min_length=1, max_length=255)
    cargo_type: str = Field(min_length=1, max_length=100)
    is_round_trip: bool = True


class TripUpdate(BaseModel):
    vehicle_id: uuid.UUID | None = None
    driver_id: uuid.UUID | None = None
    trailer_id: uuid.UUID | None = None
    origin: str | None = Field(default=None, min_length=1, max_length=255)
    destination: str | None = Field(default=None, min_length=1, max_length=255)
    cargo_type: str | None = Field(default=None, min_length=1, max_length=100)
    is_round_trip: bool | None = None
    distance_km: float | None = Field(default=None, ge=0)
    freight_cost: float | None = Field(default=None, ge=0)


class TripStart(BaseModel):
    start_odometer_km: int = Field(ge=0)


class TripAdvance(BaseModel):
    advance_payment: float = Field(ge=0)


class TripClose(BaseModel):
    end_odometer_km: int = Field(ge=0)
    freight_cost: float | None = Field(default=None, ge=0)
    advance_payment: float | None = Field(default=None, ge=0)


class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    vehicle_id: uuid.UUID
    driver_id: uuid.UUID
    trailer_id: uuid.UUID | None
    origin: str
    destination: str
    distance_km: float | None
    cargo_type: str
    is_round_trip: bool
    status: str
    start_odometer_km: int | None
    end_odometer_km: int | None
    freight_cost: float | None
    advance_payment: float
    started_at: datetime | None
    ended_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TripWithDetailsOut(TripOut):
    expenses: list[TripExpenseOut] = Field(default_factory=list)
    payroll: TripPayrollOut | None = None
