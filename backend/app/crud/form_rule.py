import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.form_rule import FormRule
from app.schemas.form_rule import FormRuleCreate, FormRuleUpdate


async def get(db: AsyncSession, rule_id: uuid.UUID, company_id: uuid.UUID) -> FormRule | None:
    result = await db.execute(
        select(FormRule).where(FormRule.id == rule_id, FormRule.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def list_for_entity(
    db: AsyncSession,
    company_id: uuid.UUID,
    entity_type: str,
    *,
    kind: str | None = None,
    only_active: bool = False,
) -> list[FormRule]:
    query = select(FormRule).where(
        FormRule.company_id == company_id, FormRule.entity_type == entity_type
    )
    if kind is not None:
        query = query.where(FormRule.kind == kind)
    if only_active:
        query = query.where(FormRule.active.is_(True))
    query = query.order_by(FormRule.order, FormRule.created_at)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create(db: AsyncSession, company_id: uuid.UUID, data: FormRuleCreate) -> FormRule:
    rule = FormRule(
        company_id=company_id,
        entity_type=data.entity_type,
        name=data.name,
        kind=data.kind,
        condition=data.condition.model_dump(),
        actions=[a.model_dump(exclude_none=True) for a in data.actions],
        active=data.active,
        order=data.order,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


async def update(db: AsyncSession, rule: FormRule, data: FormRuleUpdate) -> FormRule:
    payload = data.model_dump(exclude_unset=True)
    if "condition" in payload and data.condition is not None:
        rule.condition = data.condition.model_dump()
        payload.pop("condition")
    if "actions" in payload and data.actions is not None:
        rule.actions = [a.model_dump(exclude_none=True) for a in data.actions]
        payload.pop("actions")
    for field, value in payload.items():
        setattr(rule, field, value)
    await db.commit()
    await db.refresh(rule)
    return rule


async def delete(db: AsyncSession, rule: FormRule) -> None:
    await db.delete(rule)
    await db.commit()
