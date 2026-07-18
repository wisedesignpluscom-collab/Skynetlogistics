import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FatigueRuleUpdate(BaseModel):
    max_continuous_hours: float | None = Field(default=None, gt=0, le=24)
    max_24h_hours: float | None = Field(default=None, gt=0, le=24)
    max_7day_hours: float | None = Field(default=None, gt=0, le=168)
    night_driving_weight: float | None = Field(default=None, ge=1)
    night_start_hour: int | None = Field(default=None, ge=0, le=23)
    night_end_hour: int | None = Field(default=None, ge=0, le=23)


class FatigueRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    max_continuous_hours: float
    max_24h_hours: float
    max_7day_hours: float
    night_driving_weight: float
    night_start_hour: int
    night_end_hour: int
    created_at: datetime
    updated_at: datetime
