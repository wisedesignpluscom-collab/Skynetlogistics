import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_movement import InventoryMovement


async def create(db: AsyncSession, *, company_id: uuid.UUID, **fields) -> InventoryMovement:
    movement = InventoryMovement(company_id=company_id, **fields)
    db.add(movement)
    await db.flush()
    return movement


async def list_for_item(db: AsyncSession, item_id: uuid.UUID, company_id: uuid.UUID) -> list[InventoryMovement]:
    result = await db.execute(
        select(InventoryMovement)
        .where(InventoryMovement.company_id == company_id, InventoryMovement.item_id == item_id)
        .order_by(InventoryMovement.created_at.asc())
    )
    return list(result.scalars().all())


async def list_filtered(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    item_id: uuid.UUID | None = None,
    vehicle_id: uuid.UUID | None = None,
) -> list[InventoryMovement]:
    query = select(InventoryMovement).where(InventoryMovement.company_id == company_id)
    if item_id is not None:
        query = query.where(InventoryMovement.item_id == item_id)
    if vehicle_id is not None:
        query = query.where(InventoryMovement.vehicle_id == vehicle_id)
    query = query.order_by(InventoryMovement.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())
