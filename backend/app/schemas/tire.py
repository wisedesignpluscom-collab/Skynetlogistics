import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.tire import AXLE_DUAL_POSITIONS, AXLE_SIDES


class TireCreate(BaseModel):
    unique_code: str = Field(min_length=1, max_length=50)
    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    current_thickness_mm: float = Field(gt=0, le=99.9)
    warehouse_id: uuid.UUID | None = None
    custom_data: dict[str, Any] = Field(default_factory=dict)


class TireUpdate(BaseModel):
    brand: str | None = Field(default=None, min_length=1, max_length=100)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    current_thickness_mm: float | None = Field(default=None, gt=0, le=99.9)
    custom_data: dict[str, Any] | None = None


class TireOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    unique_code: str
    brand: str
    model: str
    current_thickness_mm: float
    status: str
    vehicle_id: uuid.UUID | None
    axle_number: int | None
    axle_side: str | None
    axle_dual_position: str | None
    warehouse_id: uuid.UUID | None
    custom_data: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class TireMovementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tire_id: uuid.UUID
    movement_type: str
    vehicle_id: uuid.UUID | None
    axle_number: int | None
    axle_side: str | None
    axle_dual_position: str | None
    warehouse_id: uuid.UUID | None
    provider_id: uuid.UUID | None
    km_at_movement: int | None
    thickness_mm: float | None
    notes: str | None
    recorded_by: uuid.UUID | None
    created_at: datetime


class TireDetailOut(TireOut):
    movements: list[TireMovementOut]
    km_current_period: int | None
    km_lifetime_total: int


class TireMovementCreate(BaseModel):
    tire_id: uuid.UUID
    movement_type: str = Field(pattern="^(instalacion|desinstalacion|envio_reparacion|envio_reencauche|retorno_taller)$")
    vehicle_id: uuid.UUID | None = None
    axle_number: int | None = Field(default=None, ge=1, le=10)
    axle_side: str | None = Field(default=None, pattern="^(" + "|".join(AXLE_SIDES) + ")$")
    axle_dual_position: str | None = Field(default=None, pattern="^(" + "|".join(AXLE_DUAL_POSITIONS) + ")$")
    warehouse_id: uuid.UUID | None = None
    provider_id: uuid.UUID | None = None
    thickness_mm: float | None = Field(default=None, gt=0, le=99.9)
    notes: str | None = Field(default=None, max_length=2000)


class TireMovementBatchItem(BaseModel):
    tire_id: uuid.UUID
    axle_number: int | None = Field(default=None, ge=1, le=10)
    axle_side: str | None = Field(default=None, pattern="^(" + "|".join(AXLE_SIDES) + ")$")
    axle_dual_position: str | None = Field(default=None, pattern="^(" + "|".join(AXLE_DUAL_POSITIONS) + ")$")
    thickness_mm: float | None = Field(default=None, gt=0, le=99.9)


class TireMovementBatchCreate(BaseModel):
    movement_type: str = Field(pattern="^(instalacion|desinstalacion|envio_reparacion|envio_reencauche|retorno_taller)$")
    items: list[TireMovementBatchItem] = Field(min_length=1)
    vehicle_id: uuid.UUID | None = None
    warehouse_id: uuid.UUID | None = None
    provider_id: uuid.UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)


class TirePerformanceRow(BaseModel):
    brand: str
    model: str
    end_reason: str
    sample_count: int
    avg_km: float
