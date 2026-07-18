import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExpenseConceptBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    default_limit: float | None = Field(default=None, ge=0)


class ExpenseConceptCreate(ExpenseConceptBase):
    pass


class ExpenseConceptUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    default_limit: float | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ExpenseConceptOut(ExpenseConceptBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
