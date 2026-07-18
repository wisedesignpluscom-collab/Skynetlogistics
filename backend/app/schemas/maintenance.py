import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.maintenance_task import MAINTENANCE_TASK_STATUSES, MAINTENANCE_TYPES, SCHEDULED_BY_OPTIONS


class MaintenanceTaskCreate(BaseModel):
    vehicle_id: uuid.UUID
    type: str = Field(pattern="^(" + "|".join(MAINTENANCE_TYPES) + ")$")
    scheduled_by: str = Field(pattern="^(" + "|".join(SCHEDULED_BY_OPTIONS) + ")$")
    due_date: date | None = None
    due_km: int | None = Field(default=None, ge=0)
    responsible_id: uuid.UUID | None = None
    description: str | None = None

    @model_validator(mode="after")
    def check_due_matches_scheduled_by(self) -> "MaintenanceTaskCreate":
        if self.scheduled_by == "tiempo" and self.due_date is None:
            raise ValueError("due_date es requerido cuando scheduled_by='tiempo'")
        if self.scheduled_by == "km" and self.due_km is None:
            raise ValueError("due_km es requerido cuando scheduled_by='km'")
        return self


class MaintenanceTaskUpdate(BaseModel):
    status: str | None = Field(default=None, pattern="^(" + "|".join(MAINTENANCE_TASK_STATUSES) + ")$")
    due_date: date | None = None
    due_km: int | None = Field(default=None, ge=0)
    responsible_id: uuid.UUID | None = None
    description: str | None = None


class MaintenanceTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    vehicle_id: uuid.UUID
    type: str
    scheduled_by: str
    due_date: date | None
    due_km: int | None
    status: str
    responsible_id: uuid.UUID | None
    description: str | None
    created_at: datetime
    updated_at: datetime


class MaintenanceRecordCreate(BaseModel):
    cost_labor: float = Field(ge=0)
    cost_parts: float = Field(ge=0)
    provider_id: uuid.UUID | None = None
    notes: str | None = None


class MaintenanceRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    cost_labor: float
    cost_parts: float
    provider_id: uuid.UUID | None
    completed_at: datetime
    notes: str | None
    created_at: datetime


class MaintenanceTaskWithRecordsOut(MaintenanceTaskOut):
    records: list[MaintenanceRecordOut] = Field(default_factory=list)
