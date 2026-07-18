import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GPSProviderVehicleMapCreate(BaseModel):
    vehicle_id: uuid.UUID
    external_device_id: str = Field(min_length=1, max_length=100)


class GPSProviderVehicleMapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    provider_id: uuid.UUID
    vehicle_id: uuid.UUID
    external_device_id: str
    created_at: datetime
