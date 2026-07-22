import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vrp_run import VrpRun


async def get(db: AsyncSession, run_id: uuid.UUID, company_id: uuid.UUID) -> VrpRun | None:
    result = await db.execute(
        select(VrpRun).where(VrpRun.id == run_id, VrpRun.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def create(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    input_stops: list[dict],
    cargo_type: str,
    vehicle_ids_considered: list[str],
    proposed_assignment: list[dict],
    created_by: uuid.UUID,
) -> VrpRun:
    run = VrpRun(
        company_id=company_id,
        input_stops=input_stops,
        cargo_type=cargo_type,
        vehicle_ids_considered=vehicle_ids_considered,
        proposed_assignment=proposed_assignment,
        created_by=created_by,
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


async def mark_confirmed(db: AsyncSession, run: VrpRun, *, result_trip_ids: list[str]) -> VrpRun:
    run.status = "confirmado"
    run.result_trip_ids = result_trip_ids
    await db.commit()
    await db.refresh(run)
    return run


async def mark_discarded(db: AsyncSession, run: VrpRun) -> VrpRun:
    run.status = "descartado"
    await db.commit()
    await db.refresh(run)
    return run
