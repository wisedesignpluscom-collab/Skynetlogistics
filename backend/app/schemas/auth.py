from pydantic import BaseModel, EmailStr

from app.schemas.user import UserWithRoleOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginResponse(TokenPair):
    user: UserWithRoleOut


class MeResponse(BaseModel):
    user: UserWithRoleOut
    permissions: dict[str, list[str]]
