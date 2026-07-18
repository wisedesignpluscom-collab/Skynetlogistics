import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TripExpenseCreate(BaseModel):
    concept_id: uuid.UUID
    amount: float = Field(ge=0)
    notes: str | None = None


class TripExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trip_id: uuid.UUID
    concept_id: uuid.UUID
    amount: float
    notes: str | None
    recorded_by: uuid.UUID | None
    created_at: datetime
