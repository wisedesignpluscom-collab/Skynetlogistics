import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.maintenance_record import MaintenanceRecord
from app.models.maintenance_task import MaintenanceTask
from app.schemas.maintenance import MaintenanceRecordCreate, MaintenanceTaskCreate, MaintenanceTaskUpdate


async def get(db: AsyncSession, task_id: uuid.UUID, company_id: uuid.UUID) -> MaintenanceTask | None:
    result = await db.execute(
        select(MaintenanceTask).where(
            MaintenanceTask.id == task_id, MaintenanceTask.company_id == company_id
        )
    )
    return result.scalar_one_or_none()


async def get_with_records(
    db: AsyncSession, task_id: uuid.UUID, company_id: uuid.UUID
) -> MaintenanceTask | None:
    result = await db.execute(
        select(MaintenanceTask)
        .options(selectinload(MaintenanceTask.records))
        .where(MaintenanceTask.id == task_id, MaintenanceTask.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    page: int,
    page_size: int,
    vehicle_id: uuid.UUID | None = None,
    status: str | None = None,
    type: str | None = None,
) -> tuple[list[MaintenanceTask], int]:
    query = select(MaintenanceTask).where(MaintenanceTask.company_id == company_id)
    count_query = (
        select(func.count()).select_from(MaintenanceTask).where(MaintenanceTask.company_id == company_id)
    )

    if vehicle_id:
        query = query.where(MaintenanceTask.vehicle_id == vehicle_id)
        count_query = count_query.where(MaintenanceTask.vehicle_id == vehicle_id)
    if status:
        query = query.where(MaintenanceTask.status == status)
        count_query = count_query.where(MaintenanceTask.status == status)
    if type:
        query = query.where(MaintenanceTask.type == type)
        count_query = count_query.where(MaintenanceTask.type == type)

    total = (await db.execute(count_query)).scalar_one()
    query = (
        query.order_by(MaintenanceTask.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def list_for_vehicle_with_records(
    db: AsyncSession, vehicle_id: uuid.UUID, company_id: uuid.UUID
) -> list[MaintenanceTask]:
    result = await db.execute(
        select(MaintenanceTask)
        .options(selectinload(MaintenanceTask.records))
        .where(MaintenanceTask.vehicle_id == vehicle_id, MaintenanceTask.company_id == company_id)
        .order_by(MaintenanceTask.created_at.desc())
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession, company_id: uuid.UUID, data: MaintenanceTaskCreate
) -> MaintenanceTask:
    task = MaintenanceTask(company_id=company_id, **data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update(db: AsyncSession, task: MaintenanceTask, data: MaintenanceTaskUpdate) -> MaintenanceTask:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


async def complete(
    db: AsyncSession, task: MaintenanceTask, data: MaintenanceRecordCreate
) -> MaintenanceTask:
    record = MaintenanceRecord(
        task_id=task.id,
        cost_labor=data.cost_labor,
        cost_parts=data.cost_parts,
        provider_id=data.provider_id,
        notes=data.notes,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(record)
    task.status = "completada"
    await db.commit()
    await db.refresh(task)
    return task
