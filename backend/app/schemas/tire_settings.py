import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TireSettingsUpdate(BaseModel):
    disparity_threshold_mm: float | None = Field(default=None, gt=0, le=20)


class TireSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    disparity_threshold_mm: float
    created_at: datetime
    updated_at: datetime
