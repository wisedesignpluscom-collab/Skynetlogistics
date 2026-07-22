import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.vehicle_document import VehicleDocument
from app.schemas.vehicle_document import VehicleDocumentCreate, VehicleDocumentUpdate


async def get(db: AsyncSession, document_id: uuid.UUID, company_id: uuid.UUID) -> VehicleDocument | None:
    result = await db.execute(
        select(VehicleDocument)
        .options(selectinload(VehicleDocument.document_type))
        .where(VehicleDocument.id == document_id, VehicleDocument.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def list_for_vehicle(
    db: AsyncSession, vehicle_id: uuid.UUID, company_id: uuid.UUID
) -> list[VehicleDocument]:
    result = await db.execute(
        select(VehicleDocument)
        .options(selectinload(VehicleDocument.document_type))
        .where(VehicleDocument.vehicle_id == vehicle_id, VehicleDocument.company_id == company_id)
        .order_by(VehicleDocument.created_at.desc())
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession, company_id: uuid.UUID, vehicle_id: uuid.UUID, data: VehicleDocumentCreate
) -> VehicleDocument:
    document = VehicleDocument(company_id=company_id, vehicle_id=vehicle_id, **data.model_dump())
    db.add(document)
    await db.commit()
    await db.refresh(document, attribute_names=["document_type"])
    return document


async def update(
    db: AsyncSession, document: VehicleDocument, data: VehicleDocumentUpdate
) -> VehicleDocument:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    await db.commit()
    await db.refresh(document, attribute_names=["document_type"])
    return document


async def delete(db: AsyncSession, document: VehicleDocument) -> None:
    await db.delete(document)
    await db.commit()
