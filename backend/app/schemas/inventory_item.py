import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InventoryItemCreate(BaseModel):
    warehouse_id: uuid.UUID
    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    unit: str = Field(default="unidad", min_length=1, max_length=20)
    min_stock: float = Field(default=0, ge=0)
    unit_cost: float = Field(default=0, ge=0)
    custom_data: dict[str, Any] = Field(default_factory=dict)


class InventoryItemUpdate(BaseModel):
    warehouse_id: uuid.UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=200)
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    min_stock: float | None = Field(default=None, ge=0)
    unit_cost: float | None = Field(default=None, ge=0)
    custom_data: dict[str, Any] | None = None


class InventoryItemOut(BaseModel):
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
    custom_data: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class InventoryMovementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    item_id: uuid.UUID
    vehicle_id: uuid.UUID | None
    provider_id: uuid.UUID | None
    movement_type: str
    quantity: float
    unit_cost: float | None
    invoice_number: str | None
    tax_percentage: float | None
    reference_doc: str | None
    notes: str | None
    recorded_by: uuid.UUID | None
    created_at: datetime


class InventoryItemDetailOut(InventoryItemOut):
    movements: list[InventoryMovementOut]


class InventoryMovementCreate(BaseModel):
    item_id: uuid.UUID
    movement_type: str = Field(pattern="^(entrada|salida|ajuste)$")
    quantity: float
    vehicle_id: uuid.UUID | None = None
    provider_id: uuid.UUID | None = None
    unit_cost: float | None = Field(default=None, ge=0)
    invoice_number: str | None = Field(default=None, max_length=100)
    tax_percentage: float | None = Field(default=None, ge=0, le=100)
    reference_doc: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=2000)
