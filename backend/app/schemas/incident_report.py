import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.incident_report import INCIDENT_SEVERITIES, INCIDENT_STATUSES, INCIDENT_TYPES


class IncidentReportCreate(BaseModel):
    vehicle_id: uuid.UUID | None = None
    trip_id: uuid.UUID | None = None
    type: str = Field(pattern="^(" + "|".join(INCIDENT_TYPES) + ")$")
    severity: str = Field(pattern="^(" + "|".join(INCIDENT_SEVERITIES) + ")$")
    description: str = Field(min_length=1)
    lat: float | None = None
    lng: float | None = None


class IncidentReportUpdate(BaseModel):
    status: str = Field(pattern="^(" + "|".join(INCIDENT_STATUSES) + ")$")
    resolution_notes: str | None = None


class IncidentReportAttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_report_id: uuid.UUID
    file_url: str
    uploaded_by: uuid.UUID | None
    created_at: datetime


class IncidentReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    driver_id: uuid.UUID
    vehicle_id: uuid.UUID | None
    trip_id: uuid.UUID | None
    type: str
    severity: str
    status: str
    description: str
    lat: float | None
    lng: float | None
    resolved_at: datetime | None
    resolved_by: uuid.UUID | None
    resolution_notes: str | None
    created_at: datetime
    updated_at: datetime
