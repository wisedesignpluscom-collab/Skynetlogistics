from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    # Necesario en modo async: sin esto, columnas con server_default/onupdate
    # (created_at, updated_at) quedan "expired" tras el flush y su lectura
    # posterior dispara un lazy-load síncrono que rompe (MissingGreenlet).
    __mapper_args__ = {"eager_defaults": True}


engine = create_async_engine(settings.database_url, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
