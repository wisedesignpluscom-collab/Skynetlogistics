import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver_document_type import DriverDocumentType
from app.schemas.driver_document import DriverDocumentTypeCreate, DriverDocumentTypeUpdate


async def get(db: AsyncSession, type_id: uuid.UUID, company_id: uuid.UUID) -> DriverDocumentType | None:
    result = await db.execute(
        select(DriverDocumentType).where(
            DriverDocumentType.id == type_id, DriverDocumentType.company_id == company_id
        )
    )
    return result.scalar_one_or_none()


async def list_all_for_company(db: AsyncSession, company_id: uuid.UUID) -> list[DriverDocumentType]:
    result = await db.execute(
        select(DriverDocumentType)
        .where(DriverDocumentType.company_id == company_id)
        .order_by(DriverDocumentType.name)
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession, company_id: uuid.UUID, data: DriverDocumentTypeCreate
) -> DriverDocumentType:
    doc_type = DriverDocumentType(company_id=company_id, **data.model_dump())
    db.add(doc_type)
    await db.commit()
    await db.refresh(doc_type)
    return doc_type


async def update(
    db: AsyncSession, doc_type: DriverDocumentType, data: DriverDocumentTypeUpdate
) -> DriverDocumentType:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doc_type, field, value)
    await db.commit()
    await db.refresh(doc_type)
    return doc_type


async def delete(db: AsyncSession, doc_type: DriverDocumentType) -> None:
    await db.delete(doc_type)
    await db.commit()
