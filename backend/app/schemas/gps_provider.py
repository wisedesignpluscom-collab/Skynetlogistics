import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.gps_provider import INGESTION_MODES


class GPSProviderCreate(BaseModel):
    provider_name: str = Field(min_length=1, max_length=100)
    adapter_type: str = Field(min_length=1, max_length=50)
    api_credentials: dict[str, Any] = Field(default_factory=dict)
    ingestion_mode: str = Field(pattern="^(" + "|".join(INGESTION_MODES) + ")$")
    polling_interval_seconds: int | None = Field(default=None, ge=10)


class GPSProviderUpdate(BaseModel):
    provider_name: str | None = Field(default=None, min_length=1, max_length=100)
    api_credentials: dict[str, Any] | None = None
    polling_interval_seconds: int | None = Field(default=None, ge=10)
    is_active: bool | None = None


class GPSProviderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    provider_name: str
    adapter_type: str
    ingestion_mode: str
    polling_interval_seconds: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class GPSProviderCreatedOut(GPSProviderOut):
    """Se devuelve solo en la creación / regeneración de token — incluye el token en claro
    una única vez; después solo se guarda su hash y no se puede volver a mostrar."""

    webhook_token: str | None = None
