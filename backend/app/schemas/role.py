import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    permissions: dict[str, list[str]] = Field(default_factory=dict)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    permissions: dict[str, list[str]] | None = None


class RoleOut(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    is_system: bool
    created_at: datetime
    updated_at: datetime
