import uuid

from sqlalchemy import func, select, text
from sqlalchemy import update as sa_update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert


async def list_paginated(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    page: int,
    page_size: int,
    status: str | None = None,
    severity: str | None = None,
) -> tuple[list[Alert], int]:
    query = select(Alert).where(Alert.company_id == company_id)
    count_query = select(func.count()).select_from(Alert).where(Alert.company_id == company_id)

    if status:
        query = query.where(Alert.status == status)
        count_query = count_query.where(Alert.status == status)
    if severity:
        query = query.where(Alert.severity == severity)
        count_query = count_query.where(Alert.severity == severity)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(Alert.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def get(db: AsyncSession, alert_id: uuid.UUID, company_id: uuid.UUID) -> Alert | None:
    result = await db.execute(select(Alert).where(Alert.id == alert_id, Alert.company_id == company_id))
    return result.scalar_one_or_none()


async def unread_count(db: AsyncSession, company_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(Alert)
        .where(Alert.company_id == company_id, Alert.status == "no_leida")
    )
    return result.scalar_one()


async def mark_read(db: AsyncSession, alert: Alert) -> Alert:
    alert.status = "leida"
    await db.commit()
    await db.refresh(alert)
    return alert


async def mark_all_read(db: AsyncSession, company_id: uuid.UUID) -> None:
    await db.execute(
        sa_update(Alert)
        .where(Alert.company_id == company_id, Alert.status == "no_leida")
        .values(status="leida")
    )
    await db.commit()


async def create_if_not_exists(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    type: str,
    entity_type: str,
    entity_id: uuid.UUID,
    message: str,
    severity: str,
) -> bool:
    """Inserta la alerta salvo que ya exista una sin leer del mismo (company_id, type, entity_id).

    Se apoya en el índice único parcial `uq_alerts_unread_dedupe` (status='no_leida').
    Devuelve True si insertó una alerta nueva, False si ya existía y se omitió.
    """
    stmt = (
        pg_insert(Alert)
        .values(
            company_id=company_id,
            type=type,
            entity_type=entity_type,
            entity_id=entity_id,
            message=message,
            severity=severity,
            status="no_leida",
        )
        .on_conflict_do_nothing(
            index_elements=["company_id", "type", "entity_id"],
            index_where=text("status = 'no_leida'"),
        )
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
