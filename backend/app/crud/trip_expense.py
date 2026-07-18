import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.trip_expense import TripExpense
from app.schemas.trip_expense import TripExpenseCreate


async def get(db: AsyncSession, expense_id: uuid.UUID, trip_id: uuid.UUID) -> TripExpense | None:
    result = await db.execute(
        select(TripExpense).where(TripExpense.id == expense_id, TripExpense.trip_id == trip_id)
    )
    return result.scalar_one_or_none()


async def list_for_trip(db: AsyncSession, trip_id: uuid.UUID) -> list[TripExpense]:
    result = await db.execute(
        select(TripExpense)
        .options(selectinload(TripExpense.concept))
        .where(TripExpense.trip_id == trip_id)
        .order_by(TripExpense.created_at.desc())
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession, trip_id: uuid.UUID, data: TripExpenseCreate, recorded_by: uuid.UUID
) -> TripExpense:
    expense = TripExpense(trip_id=trip_id, recorded_by=recorded_by, **data.model_dump())
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense


async def delete(db: AsyncSession, expense: TripExpense) -> None:
    await db.delete(expense)
    await db.commit()
