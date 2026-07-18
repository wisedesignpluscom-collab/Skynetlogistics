import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CompanyHolidayCreate(BaseModel):
    date: date
    name: str = Field(min_length=1, max_length=100)


class CompanyHolidayOut(CompanyHolidayCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
