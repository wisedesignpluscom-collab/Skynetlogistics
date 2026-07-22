import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.custom_field import CustomFieldDefinition
from app.schemas.custom_field import CustomFieldDefinitionCreate, CustomFieldDefinitionUpdate


async def get(db: AsyncSession, field_id: uuid.UUID, company_id: uuid.UUID) -> CustomFieldDefinition | None:
    result = await db.execute(
        select(CustomFieldDefinition).where(
            CustomFieldDefinition.id == field_id, CustomFieldDefinition.company_id == company_id
        )
    )
    return result.scalar_one_or_none()


async def get_by_key(
    db: AsyncSession, company_id: uuid.UUID, entity_type: str, key: str
) -> CustomFieldDefinition | None:
    result = await db.execute(
        select(CustomFieldDefinition).where(
            CustomFieldDefinition.company_id == company_id,
            CustomFieldDefinition.entity_type == entity_type,
            CustomFieldDefinition.key == key,
        )
    )
    return result.scalar_one_or_none()


async def list_for_entity(
    db: AsyncSession, company_id: uuid.UUID, entity_type: str, *, only_active: bool = False
) -> list[CustomFieldDefinition]:
    query = select(CustomFieldDefinition).where(
        CustomFieldDefinition.company_id == company_id,
        CustomFieldDefinition.entity_type == entity_type,
    )
    if only_active:
        query = query.where(CustomFieldDefinition.active.is_(True))
    query = query.order_by(CustomFieldDefinition.order, CustomFieldDefinition.created_at)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create(
    db: AsyncSession, company_id: uuid.UUID, data: CustomFieldDefinitionCreate
) -> CustomFieldDefinition:
    definition = CustomFieldDefinition(
        company_id=company_id,
        entity_type=data.entity_type,
        key=data.key,
        label=data.label,
        field_type=data.field_type,
        options=[o.model_dump() for o in data.options],
        required=data.required,
        order=data.order,
        active=data.active,
        help_text=data.help_text,
    )
    db.add(definition)
    await db.commit()
    await db.refresh(definition)
    return definition


async def update(
    db: AsyncSession, definition: CustomFieldDefinition, data: CustomFieldDefinitionUpdate
) -> CustomFieldDefinition:
    payload = data.model_dump(exclude_unset=True)
    if "options" in payload and payload["options"] is not None:
        payload["options"] = [o if isinstance(o, dict) else o.model_dump() for o in data.options]
    for field, value in payload.items():
        setattr(definition, field, value)
    await db.commit()
    await db.refresh(definition)
    return definition


async def delete(db: AsyncSession, definition: CustomFieldDefinition) -> None:
    await db.delete(definition)
    await db.commit()
