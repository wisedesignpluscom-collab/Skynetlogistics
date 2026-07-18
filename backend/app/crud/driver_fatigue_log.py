import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver_fatigue_log import DriverFatigueLog


async def get_latest_for_driver(db: AsyncSession, driver_id: uuid.UUID) -> DriverFatigueLog | None:
    result = await db.execute(
        select(DriverFatigueLog)
        .where(DriverFatigueLog.driver_id == driver_id)
        .order_by(DriverFatigueLog.date.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_for_drivers(
    db: AsyncSession, driver_ids: list[uuid.UUID]
) -> dict[uuid.UUID, DriverFatigueLog]:
    if not driver_ids:
        return {}
    result = await db.execute(
        select(DriverFatigueLog)
        .where(DriverFatigueLog.driver_id.in_(driver_ids))
        .order_by(DriverFatigueLog.driver_id, DriverFatigueLog.date.desc())
    )
    latest_by_driver: dict[uuid.UUID, DriverFatigueLog] = {}
    for log in result.scalars().all():
        if log.driver_id not in latest_by_driver:
            latest_by_driver[log.driver_id] = log
    return latest_by_driver


async def list_history(
    db: AsyncSession, driver_id: uuid.UUID, *, date_from: date, date_to: date
) -> list[DriverFatigueLog]:
    result = await db.execute(
        select(DriverFatigueLog)
        .where(
            DriverFatigueLog.driver_id == driver_id,
            DriverFatigueLog.date >= date_from,
            DriverFatigueLog.date <= date_to,
        )
        .order_by(DriverFatigueLog.date.asc())
    )
    return list(result.scalars().all())


async def upsert(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    driver_id: uuid.UUID,
    log_date: date,
    continuous_driving_min: int,
    total_24h_min: int,
    total_7day_min: int,
    night_driving_min: int,
    risk_score: float,
    risk_level: str,
) -> None:
    stmt = (
        pg_insert(DriverFatigueLog)
        .values(
            company_id=company_id,
            driver_id=driver_id,
            date=log_date,
            continuous_driving_min=continuous_driving_min,
            total_24h_min=total_24h_min,
            total_7day_min=total_7day_min,
            night_driving_min=night_driving_min,
            risk_score=risk_score,
            risk_level=risk_level,
        )
        .on_conflict_do_update(
            index_elements=["driver_id", "date"],
            set_={
                "continuous_driving_min": continuous_driving_min,
                "total_24h_min": total_24h_min,
                "total_7day_min": total_7day_min,
                "night_driving_min": night_driving_min,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "computed_at": func.now(),
            },
        )
    )
    await db.execute(stmt)
    await db.commit()
