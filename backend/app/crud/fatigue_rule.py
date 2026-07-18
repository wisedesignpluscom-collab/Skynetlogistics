import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fatigue_rule import FatigueRule
from app.schemas.fatigue_rule import FatigueRuleUpdate


async def get_by_company(db: AsyncSession, company_id: uuid.UUID) -> FatigueRule | None:
    result = await db.execute(select(FatigueRule).where(FatigueRule.company_id == company_id))
    return result.scalar_one_or_none()


async def get_or_create(db: AsyncSession, company_id: uuid.UUID) -> FatigueRule:
    rule = await get_by_company(db, company_id)
    if rule is not None:
        return rule
    rule = FatigueRule(company_id=company_id)
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


async def update(db: AsyncSession, rule: FatigueRule, data: FatigueRuleUpdate) -> FatigueRule:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    await db.commit()
    await db.refresh(rule)
    return rule
