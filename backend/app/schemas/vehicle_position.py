import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VehiclePositionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vehicle_id: uuid.UUID
    company_id: uuid.UUID
    provider_id: uuid.UUID
    timestamp: datetime
    lat: float
    lng: float
    speed_kmh: float | None
    odometer_km: int | None
    ignition_status: bool | None
    heading: int | None
