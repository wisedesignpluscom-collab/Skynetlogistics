import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    type: str
    entity_type: str
    entity_id: uuid.UUID
    message: str
    severity: str
    status: str
    created_at: datetime


class UnreadCountOut(BaseModel):
    count: int
