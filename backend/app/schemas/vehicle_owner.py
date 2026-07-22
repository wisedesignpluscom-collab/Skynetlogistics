import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class VehicleOwnerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    tax_id: str | None = Field(default=None, max_length=50)
    contact_person: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    notes: str | None = Field(default=None, max_length=2000)


class VehicleOwnerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    tax_id: str | None = Field(default=None, max_length=50)
    contact_person: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    notes: str | None = Field(default=None, max_length=2000)
    is_active: bool | None = None


class VehicleOwnerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    tax_id: str | None
    contact_person: str | None
    phone: str | None
    email: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
