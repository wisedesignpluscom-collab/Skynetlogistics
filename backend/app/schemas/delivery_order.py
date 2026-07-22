import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.delivery_order import DELIVERY_ORDER_STATUSES


class DeliveryOrderItemIn(BaseModel):
    goods_id: uuid.UUID
    quantity: float = Field(gt=0)


class DeliveryOrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    goods_id: uuid.UUID
    quantity: float


class DeliveryOrderCreate(BaseModel):
    client_id: uuid.UUID
    address: str = Field(min_length=1, max_length=500)
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    priority: int = Field(default=0, ge=0)
    time_window_start: datetime | None = None
    time_window_end: datetime | None = None
    notes: str | None = None
    custom_data: dict[str, Any] = Field(default_factory=dict)
    items: list[DeliveryOrderItemIn] = Field(min_length=1)


class DeliveryOrderUpdate(BaseModel):
    address: str | None = Field(default=None, min_length=1, max_length=500)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    priority: int | None = Field(default=None, ge=0)
    time_window_start: datetime | None = None
    time_window_end: datetime | None = None
    notes: str | None = None
    custom_data: dict[str, Any] | None = None


class DeliveryOrderAssign(BaseModel):
    trip_id: uuid.UUID


class DeliveryOrderDeliver(BaseModel):
    delivery_proof_url: str | None = Field(default=None, max_length=500)
    notes: str | None = None


class DeliveryOrderFail(BaseModel):
    failure_reason: str = Field(min_length=1)
    return_stock: bool = True


class DeliveryOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    client_id: uuid.UUID
    trip_id: uuid.UUID | None
    address: str
    lat: float
    lng: float
    status: str
    priority: int
    time_window_start: datetime | None
    time_window_end: datetime | None
    notes: str | None
    delivered_at: datetime | None
    delivered_by: uuid.UUID | None
    delivery_proof_url: str | None
    failure_reason: str | None
    created_by: uuid.UUID | None
    custom_data: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
    items: list[DeliveryOrderItemOut]


VALID_STATUSES = set(DELIVERY_ORDER_STATUSES)
