import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Workflow
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate


async def get(db: AsyncSession, workflow_id: uuid.UUID, company_id: uuid.UUID) -> Workflow | None:
    result = await db.execute(
        select(Workflow).where(Workflow.id == workflow_id, Workflow.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def list_for_entity(
    db: AsyncSession,
    company_id: uuid.UUID,
    entity_type: str,
    *,
    event: str | None = None,
    only_active: bool = False,
) -> list[Workflow]:
    query = select(Workflow).where(Workflow.company_id == company_id, Workflow.entity_type == entity_type)
    if event is not None:
        query = query.where(Workflow.event == event)
    if only_active:
        query = query.where(Workflow.active.is_(True))
    query = query.order_by(Workflow.order, Workflow.created_at)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create(db: AsyncSession, company_id: uuid.UUID, data: WorkflowCreate) -> Workflow:
    workflow = Workflow(
        company_id=company_id,
        entity_type=data.entity_type,
        name=data.name,
        event=data.event,
        condition=data.condition.model_dump(),
        actions=[a.model_dump(exclude_none=True) for a in data.actions],
        active=data.active,
        order=data.order,
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow


async def update(db: AsyncSession, workflow: Workflow, data: WorkflowUpdate) -> Workflow:
    payload = data.model_dump(exclude_unset=True)
    if "condition" in payload and data.condition is not None:
        workflow.condition = data.condition.model_dump()
        payload.pop("condition")
    if "actions" in payload and data.actions is not None:
        workflow.actions = [a.model_dump(exclude_none=True) for a in data.actions]
        payload.pop("actions")
    for field, value in payload.items():
        setattr(workflow, field, value)
    await db.commit()
    await db.refresh(workflow)
    return workflow


async def delete(db: AsyncSession, workflow: Workflow) -> None:
    await db.delete(workflow)
    await db.commit()
