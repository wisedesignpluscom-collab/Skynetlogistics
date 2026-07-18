from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.crud import refresh_token as refresh_token_crud
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    MeResponse,
    RefreshRequest,
    TokenPair,
)
from app.utils.permissions import SUPERADMIN_PERMISSIONS

router = APIRouter(prefix="/auth", tags=["auth"])

INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Email o password incorrectos"
)


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    user = await user_crud.get_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise INVALID_CREDENTIALS
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuario inactivo")
    if not user.company.is_active and not user.is_superadmin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "La empresa está inactiva")

    access_token = create_access_token(
        user_id=user.id, company_id=user.company_id, is_superadmin=user.is_superadmin
    )
    _, raw_refresh_token = await refresh_token_crud.create_for_user(db, user.id)
    await user_crud.touch_last_login(db, user)

    return LoginResponse(access_token=access_token, refresh_token=raw_refresh_token, user=user)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    token = await refresh_token_crud.get_valid_by_raw_token(db, payload.refresh_token)
    if token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token inválido o expirado")

    user = await user_crud.get_by_id_any_company(db, token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token inválido o expirado")

    # Rotación: se revoca el token usado y se emite un par nuevo.
    await refresh_token_crud.revoke(db, token)
    access_token = create_access_token(
        user_id=user.id, company_id=user.company_id, is_superadmin=user.is_superadmin
    )
    _, raw_refresh_token = await refresh_token_crud.create_for_user(db, user.id)

    return TokenPair(access_token=access_token, refresh_token=raw_refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, db: AsyncSession = Depends(get_db)) -> None:
    token = await refresh_token_crud.get_valid_by_raw_token(db, payload.refresh_token)
    if token is not None:
        await refresh_token_crud.revoke(db, token)


@router.get("/me", response_model=MeResponse)
async def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    permissions = SUPERADMIN_PERMISSIONS if current_user.is_superadmin else current_user.role.permissions
    return MeResponse(user=current_user, permissions=permissions)
