import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DeliveryGoodsCreate(BaseModel):
    warehouse_id: uuid.UUID
    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    unit: str = Field(default="unidad", min_length=1, max_length=20)
    min_stock: float = Field(default=0, ge=0)
    unit_cost: float = Field(default=0, ge=0)
    weight_kg_per_unit: float = Field(default=0, ge=0)
    volume_m3_per_unit: float = Field(default=0, ge=0)
    custom_data: dict[str, Any] = Field(default_factory=dict)


class DeliveryGoodsUpdate(BaseModel):
    warehouse_id: uuid.UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=200)
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    min_stock: float | None = Field(default=None, ge=0)
    unit_cost: float | None = Field(default=None, ge=0)
    weight_kg_per_unit: float | None = Field(default=None, ge=0)
    volume_m3_per_unit: float | None = Field(default=None, ge=0)
    custom_data: dict[str, Any] | None = None


class DeliveryGoodsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    warehouse_id: uuid.UUID
    sku: str
    name: str
    unit: str
    quantity: float
    min_stock: float
    unit_cost: float
    weight_kg_per_unit: float
    volume_m3_per_unit: float
    custom_data: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class DeliveryGoodsMovementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    goods_id: uuid.UUID
    movement_type: str
    quantity: float
    unit_cost: float | None
    reference_doc: str | None
    notes: str | None
    recorded_by: uuid.UUID | None
    created_at: datetime


class DeliveryGoodsDetailOut(DeliveryGoodsOut):
    movements: list[DeliveryGoodsMovementOut]


class DeliveryGoodsMovementCreate(BaseModel):
    goods_id: uuid.UUID
    movement_type: str = Field(pattern="^(entrada|salida|ajuste)$")
    quantity: float
    unit_cost: float | None = Field(default=None, ge=0)
    reference_doc: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=2000)
