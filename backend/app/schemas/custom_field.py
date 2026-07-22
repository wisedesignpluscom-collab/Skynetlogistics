import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.custom_field import CUSTOM_FIELD_ENTITY_TYPES, CUSTOM_FIELD_TYPES

_KEY_PATTERN = r"^[a-z][a-z0-9_]*$"


class CustomFieldOption(BaseModel):
    value: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=150)


class CustomFieldDefinitionBase(BaseModel):
    label: str = Field(min_length=1, max_length=150)
    field_type: str = Field(pattern="^(" + "|".join(CUSTOM_FIELD_TYPES) + ")$")
    options: list[CustomFieldOption] = Field(default_factory=list)
    required: bool = False
    order: int = 0
    active: bool = True
    help_text: str | None = None

    @field_validator("options")
    @classmethod
    def _unique_option_values(cls, v: list[CustomFieldOption]) -> list[CustomFieldOption]:
        values = [o.value for o in v]
        if len(values) != len(set(values)):
            raise ValueError("Las opciones no pueden repetir 'value'")
        return v


class CustomFieldDefinitionCreate(CustomFieldDefinitionBase):
    entity_type: str = Field(pattern="^(" + "|".join(CUSTOM_FIELD_ENTITY_TYPES) + ")$")
    key: str = Field(min_length=1, max_length=50, pattern=_KEY_PATTERN)


class CustomFieldDefinitionUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=150)
    options: list[CustomFieldOption] | None = None
    required: bool | None = None
    order: int | None = None
    active: bool | None = None
    help_text: str | None = None


class CustomFieldDefinitionOut(CustomFieldDefinitionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    entity_type: str
    key: str
    created_at: datetime
    updated_at: datetime
