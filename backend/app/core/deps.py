import uuid
from collections.abc import Callable, Coroutine

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.crud import user as user_crud
from app.models.user import User
from app.utils.permissions import has_permission

# tokenUrl es solo informativo para la doc de OpenAPI; el login real es JSON en /auth/login.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudo validar la credencial",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if token is None:
        raise CREDENTIALS_ERROR
    try:
        payload = decode_access_token(token)
        user_id = uuid.UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise CREDENTIALS_ERROR from None

    user = await user_crud.get_by_id_any_company(db, user_id)
    if user is None or not user.is_active:
        raise CREDENTIALS_ERROR
    if not user.company.is_active and not user.is_superadmin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "La empresa está inactiva")
    return user


async def get_current_superadmin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superadmin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Requiere privilegios de superadmin")
    return current_user


def require_permission(module: str, action: str) -> Callable[..., Coroutine[None, None, User]]:
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superadmin:
            return current_user
        if not has_permission(current_user.role.permissions, module, action):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"No tienes permiso '{action}' sobre el módulo '{module}'",
            )
        return current_user

    return checker
