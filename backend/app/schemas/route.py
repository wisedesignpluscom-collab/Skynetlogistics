import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RouteComputeRequest(BaseModel):
    origin_lat: float = Field(ge=-90, le=90)
    origin_lng: float = Field(ge=-180, le=180)
    destination_lat: float = Field(ge=-90, le=90)
    destination_lng: float = Field(ge=-180, le=180)


class RouteRecalculationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    route_plan_id: uuid.UUID
    reason: str
    deviation_m: float | None
    trigger_lat: float | None
    trigger_lng: float | None
    new_distance_km: float
    new_duration_min: int
    new_route_data: list
    created_at: datetime


class RoutePlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    trip_id: uuid.UUID
    origin_lat: float
    origin_lng: float
    destination_lat: float
    destination_lng: float
    geometry: list
    waypoints: list
    calculated_distance_km: float
    calculated_duration_min: int
    engine_used: str
    created_at: datetime
    updated_at: datetime


class RoutePlanDetailOut(RoutePlanOut):
    recalculations: list[RouteRecalculationOut]


class RouteSettingsUpdate(BaseModel):
    deviation_threshold_m: int | None = Field(default=None, ge=10, le=10_000)
    recalc_cooldown_min: int | None = Field(default=None, ge=0, le=1440)


class RouteSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    deviation_threshold_m: int
    recalc_cooldown_min: int
    created_at: datetime
    updated_at: datetime
