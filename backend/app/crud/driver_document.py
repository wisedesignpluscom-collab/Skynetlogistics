import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.driver_document import DriverDocument
from app.schemas.driver_document import DriverDocumentCreate, DriverDocumentUpdate


async def get(db: AsyncSession, document_id: uuid.UUID, company_id: uuid.UUID) -> DriverDocument | None:
    result = await db.execute(
        select(DriverDocument)
        .options(selectinload(DriverDocument.document_type))
        .where(DriverDocument.id == document_id, DriverDocument.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def list_for_driver(
    db: AsyncSession, driver_id: uuid.UUID, company_id: uuid.UUID
) -> list[DriverDocument]:
    result = await db.execute(
        select(DriverDocument)
        .options(selectinload(DriverDocument.document_type))
        .where(DriverDocument.driver_id == driver_id, DriverDocument.company_id == company_id)
        .order_by(DriverDocument.created_at.desc())
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession, company_id: uuid.UUID, driver_id: uuid.UUID, data: DriverDocumentCreate
) -> DriverDocument:
    document = DriverDocument(company_id=company_id, driver_id=driver_id, **data.model_dump())
    db.add(document)
    await db.commit()
    await db.refresh(document, attribute_names=["document_type"])
    return document


async def update(
    db: AsyncSession, document: DriverDocument, data: DriverDocumentUpdate
) -> DriverDocument:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    await db.commit()
    await db.refresh(document, attribute_names=["document_type"])
    return document


async def delete(db: AsyncSession, document: DriverDocument) -> None:
    await db.delete(document)
    await db.commit()
