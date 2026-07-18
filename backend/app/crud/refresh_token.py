import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    generate_refresh_token,
    hash_refresh_token,
    refresh_token_expiry,
)
from app.models.refresh_token import RefreshToken


async def create_for_user(db: AsyncSession, user_id: uuid.UUID) -> tuple[RefreshToken, str]:
    raw_token = generate_refresh_token()
    token = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(raw_token),
        expires_at=refresh_token_expiry(),
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token, raw_token


async def get_valid_by_raw_token(db: AsyncSession, raw_token: str) -> RefreshToken | None:
    token_hash = hash_refresh_token(raw_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    token = result.scalar_one_or_none()
    if token is None:
        return None
    if token.revoked or token.expires_at < datetime.now(timezone.utc):
        return None
    return token


async def revoke(db: AsyncSession, token: RefreshToken) -> None:
    token.revoked = True
    await db.commit()
