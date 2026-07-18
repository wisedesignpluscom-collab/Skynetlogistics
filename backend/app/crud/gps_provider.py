import hashlib
import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import encrypt_credentials
from app.models.gps_provider import GPSProvider
from app.schemas.gps_provider import GPSProviderCreate, GPSProviderUpdate


def generate_webhook_token() -> tuple[str, str]:
    """Devuelve (token_en_claro, hash_sha256) — el hash es lo único que se persiste."""
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    return raw_token, token_hash


async def get(db: AsyncSession, provider_id: uuid.UUID, company_id: uuid.UUID) -> GPSProvider | None:
    result = await db.execute(
        select(GPSProvider).where(GPSProvider.id == provider_id, GPSProvider.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def get_by_id_any_company(db: AsyncSession, provider_id: uuid.UUID) -> GPSProvider | None:
    result = await db.execute(select(GPSProvider).where(GPSProvider.id == provider_id))
    return result.scalar_one_or_none()


async def list_all_for_company(db: AsyncSession, company_id: uuid.UUID) -> list[GPSProvider]:
    result = await db.execute(select(GPSProvider).where(GPSProvider.company_id == company_id))
    return list(result.scalars().all())


async def create(
    db: AsyncSession, company_id: uuid.UUID, data: GPSProviderCreate
) -> tuple[GPSProvider, str | None]:
    raw_token: str | None = None
    token_hash: str | None = None
    if data.ingestion_mode == "webhook":
        raw_token, token_hash = generate_webhook_token()

    provider = GPSProvider(
        company_id=company_id,
        provider_name=data.provider_name,
        adapter_type=data.adapter_type,
        api_credentials_encrypted=encrypt_credentials(data.api_credentials),
        ingestion_mode=data.ingestion_mode,
        polling_interval_seconds=data.polling_interval_seconds,
        webhook_token_hash=token_hash,
    )
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return provider, raw_token


async def update(db: AsyncSession, provider: GPSProvider, data: GPSProviderUpdate) -> GPSProvider:
    updates = data.model_dump(exclude_unset=True, exclude={"api_credentials"})
    for field, value in updates.items():
        setattr(provider, field, value)
    if data.api_credentials is not None:
        provider.api_credentials_encrypted = encrypt_credentials(data.api_credentials)
    await db.commit()
    await db.refresh(provider)
    return provider


async def regenerate_webhook_token(db: AsyncSession, provider: GPSProvider) -> str:
    raw_token, token_hash = generate_webhook_token()
    provider.webhook_token_hash = token_hash
    await db.commit()
    await db.refresh(provider)
    return raw_token


async def delete(db: AsyncSession, provider: GPSProvider) -> None:
    await db.delete(provider)
    await db.commit()


def verify_webhook_token(provider: GPSProvider, raw_token: str) -> bool:
    if provider.webhook_token_hash is None:
        return False
    candidate_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    return secrets.compare_digest(candidate_hash, provider.webhook_token_hash)
