import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CompanyBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    tax_id: str = Field(min_length=1, max_length=50)
    plan: str = Field(default="trial", max_length=50)
    contact_person: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    mobile_phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    logo_url: str | None = Field(default=None, max_length=500)


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    tax_id: str | None = Field(default=None, min_length=1, max_length=50)
    plan: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None
    contact_person: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    mobile_phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    logo_url: str | None = Field(default=None, max_length=500)


class CompanyOut(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
