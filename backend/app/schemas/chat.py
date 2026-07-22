import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.chat import CHAT_THREAD_STATUSES


class ChatMessageCreate(BaseModel):
    message: str = Field(min_length=1)


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    thread_id: uuid.UUID
    sender_type: str
    sender_id: uuid.UUID
    message: str
    created_at: datetime


class ChatThreadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    driver_id: uuid.UUID
    incident_report_id: uuid.UUID | None
    status: str
    created_at: datetime


class ChatThreadUpdate(BaseModel):
    status: str = Field(pattern="^(" + "|".join(CHAT_THREAD_STATUSES) + ")$")
