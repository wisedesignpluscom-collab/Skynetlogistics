import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense_concept import ExpenseConcept
from app.schemas.expense_concept import ExpenseConceptCreate, ExpenseConceptUpdate


async def get(db: AsyncSession, concept_id: uuid.UUID, company_id: uuid.UUID) -> ExpenseConcept | None:
    result = await db.execute(
        select(ExpenseConcept).where(
            ExpenseConcept.id == concept_id, ExpenseConcept.company_id == company_id
        )
    )
    return result.scalar_one_or_none()


async def get_by_name(db: AsyncSession, company_id: uuid.UUID, name: str) -> ExpenseConcept | None:
    result = await db.execute(
        select(ExpenseConcept).where(ExpenseConcept.company_id == company_id, ExpenseConcept.name == name)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession, *, company_id: uuid.UUID, page: int, page_size: int
) -> tuple[list[ExpenseConcept], int]:
    query = select(ExpenseConcept).where(ExpenseConcept.company_id == company_id)
    count_query = (
        select(func.count()).select_from(ExpenseConcept).where(ExpenseConcept.company_id == company_id)
    )

    total = (await db.execute(count_query)).scalar_one()
    query = (
        query.order_by(ExpenseConcept.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(db: AsyncSession, company_id: uuid.UUID, data: ExpenseConceptCreate) -> ExpenseConcept:
    concept = ExpenseConcept(company_id=company_id, **data.model_dump())
    db.add(concept)
    await db.commit()
    await db.refresh(concept)
    return concept


async def update(db: AsyncSession, concept: ExpenseConcept, data: ExpenseConceptUpdate) -> ExpenseConcept:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(concept, field, value)
    await db.commit()
    await db.refresh(concept)
    return concept


async def delete(db: AsyncSession, concept: ExpenseConcept) -> None:
    await db.delete(concept)
    await db.commit()
