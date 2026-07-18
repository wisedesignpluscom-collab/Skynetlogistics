import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.driver import DRIVER_STATUSES


class DriverBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    license_number: str = Field(min_length=1, max_length=50)
    license_expiry: date
    phone: str | None = Field(default=None, max_length=30)


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    license_number: str | None = Field(default=None, min_length=1, max_length=50)
    license_expiry: date | None = None
    phone: str | None = Field(default=None, max_length=30)
    status: str | None = Field(default=None, pattern="^(" + "|".join(DRIVER_STATUSES) + ")$")


class DriverOut(DriverBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
