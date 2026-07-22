import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceSettingsUpdate(BaseModel):
    warning_days_threshold: int | None = Field(default=None, ge=0)
    warning_km_threshold: int | None = Field(default=None, ge=0)


class MaintenanceSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    warning_days_threshold: int
    warning_km_threshold: int
    created_at: datetime
    updated_at: datetime
