import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle_document_type import VehicleDocumentType
from app.schemas.vehicle_document import VehicleDocumentTypeCreate, VehicleDocumentTypeUpdate


async def get(db: AsyncSession, type_id: uuid.UUID, company_id: uuid.UUID) -> VehicleDocumentType | None:
    result = await db.execute(
        select(VehicleDocumentType).where(
            VehicleDocumentType.id == type_id, VehicleDocumentType.company_id == company_id
        )
    )
    return result.scalar_one_or_none()


async def list_all_for_company(db: AsyncSession, company_id: uuid.UUID) -> list[VehicleDocumentType]:
    result = await db.execute(
        select(VehicleDocumentType)
        .where(VehicleDocumentType.company_id == company_id)
        .order_by(VehicleDocumentType.name)
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession, company_id: uuid.UUID, data: VehicleDocumentTypeCreate
) -> VehicleDocumentType:
    doc_type = VehicleDocumentType(company_id=company_id, **data.model_dump())
    db.add(doc_type)
    await db.commit()
    await db.refresh(doc_type)
    return doc_type


async def update(
    db: AsyncSession, doc_type: VehicleDocumentType, data: VehicleDocumentTypeUpdate
) -> VehicleDocumentType:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doc_type, field, value)
    await db.commit()
    await db.refresh(doc_type)
    return doc_type


async def delete(db: AsyncSession, doc_type: VehicleDocumentType) -> None:
    await db.delete(doc_type)
    await db.commit()
