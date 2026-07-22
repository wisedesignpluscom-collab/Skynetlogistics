import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class VehicleDocumentTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    alert_days_before: int = Field(default=60, ge=0, le=3650)


class VehicleDocumentTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    alert_days_before: int | None = Field(default=None, ge=0, le=3650)


class VehicleDocumentTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    alert_days_before: int
    created_at: datetime
    updated_at: datetime


class VehicleDocumentCreate(BaseModel):
    document_type_id: uuid.UUID
    number: str | None = Field(default=None, max_length=100)
    expiry_date: date | None = None
    notes: str | None = None


class VehicleDocumentUpdate(BaseModel):
    document_type_id: uuid.UUID | None = None
    number: str | None = Field(default=None, max_length=100)
    expiry_date: date | None = None
    notes: str | None = None


class VehicleDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    vehicle_id: uuid.UUID
    document_type_id: uuid.UUID
    number: str | None
    expiry_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    document_type: VehicleDocumentTypeOut
