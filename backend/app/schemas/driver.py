import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.driver import DRIVER_STATUSES, PAY_PERIODS


class DriverBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    license_number: str = Field(min_length=1, max_length=50)
    license_expiry: date
    phone: str | None = Field(default=None, max_length=30)
    birth_date: date | None = None
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    secondary_phone: str | None = Field(default=None, max_length=30)
    notes: str | None = None
    base_salary: float | None = Field(default=None, ge=0)
    pay_period: str | None = Field(default=None, pattern="^(" + "|".join(PAY_PERIODS) + ")$")
    hire_date: date | None = None
    termination_date: date | None = None
    user_id: uuid.UUID | None = None
    custom_data: dict[str, Any] = Field(default_factory=dict)


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    license_number: str | None = Field(default=None, min_length=1, max_length=50)
    license_expiry: date | None = None
    phone: str | None = Field(default=None, max_length=30)
    status: str | None = Field(default=None, pattern="^(" + "|".join(DRIVER_STATUSES) + ")$")
    birth_date: date | None = None
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    secondary_phone: str | None = Field(default=None, max_length=30)
    notes: str | None = None
    base_salary: float | None = Field(default=None, ge=0)
    pay_period: str | None = Field(default=None, pattern="^(" + "|".join(PAY_PERIODS) + ")$")
    hire_date: date | None = None
    termination_date: date | None = None
    user_id: uuid.UUID | None = None
    custom_data: dict[str, Any] | None = None


class DriverOut(DriverBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    status: str
    user_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
