import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DriverFatigueLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    driver_id: uuid.UUID
    date: date
    continuous_driving_min: int
    total_24h_min: int
    total_7day_min: int
    night_driving_min: int
    risk_score: float
    risk_level: str
    computed_at: datetime


class DriverFatigueSummaryOut(BaseModel):
    driver_id: uuid.UUID
    risk_level: str | None
    risk_score: float | None
    computed_at: datetime | None
