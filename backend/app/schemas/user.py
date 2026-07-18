import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.role import RoleOut


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role_id: uuid.UUID


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    role_id: uuid.UUID | None = None
    is_active: bool | None = None


class UserPasswordUpdate(BaseModel):
    current_password: str | None = None
    new_password: str = Field(min_length=8, max_length=128)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    role_id: uuid.UUID
    is_active: bool
    is_superadmin: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserWithRoleOut(UserOut):
    role: RoleOut
