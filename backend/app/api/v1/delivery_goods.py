import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.custom_fields import validate_entity_custom_data
from app.core.deps import require_permission
from app.crud import delivery_goods as delivery_goods_crud
from app.crud import warehouse as warehouse_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.delivery_goods import (
    DeliveryGoodsCreate,
    DeliveryGoodsDetailOut,
    DeliveryGoodsMovementCreate,
    DeliveryGoodsMovementOut,
    DeliveryGoodsOut,
    DeliveryGoodsUpdate,
)
from app.services.delivery_goods_movements import InvalidDeliveryGoodsMovement, apply_movement
from app.services.workflows import run_workflows

router = APIRouter(prefix="/delivery-goods", tags=["delivery"])


@router.get("", response_model=Page[DeliveryGoodsOut])
async def list_delivery_goods(
    page: int = 1,
    page_size: int = 20,
    warehouse_id: uuid.UUID | None = None,
    search: str | None = None,
    low_stock: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("delivery", "read")),
) -> Page[DeliveryGoodsOut]:
    items, total = await delivery_goods_crud.list_paginated(
        db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        warehouse_id=warehouse_id,
        search=search,
        low_stock=low_stock,
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=DeliveryGoodsOut, status_code=status.HTTP_201_CREATED)
async def create_delivery_goods(
    payload: DeliveryGoodsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("delivery", "write")),
) -> DeliveryGoodsOut:
    if await warehouse_crud.get(db, payload.warehouse_id, current_user.company_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Almacén no encontrado")
    if await delivery_goods_crud.get_by_sku(db, current_user.company_id, payload.sku) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una mercancía con ese SKU")
    payload.custom_data = await validate_entity_custom_data(
        db, current_user.company_id, "delivery_goods", payload.custom_data, payload=payload
    )
    goods = await delivery_goods_crud.create(db, current_user.company_id, payload)
    await run_workflows(
        db, company_id=current_user.company_id, entity_type="delivery_goods", event="creado", entity=goods
    )
    return goods


@router.get("/{goods_id}", response_model=DeliveryGoodsDetailOut)
async def get_delivery_goods(
    goods_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("delivery", "read")),
) -> DeliveryGoodsDetailOut:
    goods = await delivery_goods_crud.get(db, goods_id, current_user.company_id)
    if goods is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mercancía no encontrada")
    movements = await delivery_goods_crud.list_movements(db, goods_id, current_user.company_id)
    return DeliveryGoodsDetailOut(
        **DeliveryGoodsOut.model_validate(goods).model_dump(),
        movements=list(reversed(movements)),
    )


@router.patch("/{goods_id}", response_model=DeliveryGoodsOut)
async def update_delivery_goods(
    goods_id: uuid.UUID,
    payload: DeliveryGoodsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("delivery", "write")),
) -> DeliveryGoodsOut:
    goods = await delivery_goods_crud.get(db, goods_id, current_user.company_id)
    if goods is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mercancía no encontrada")
    if payload.warehouse_id is not None:
        if await warehouse_crud.get(db, payload.warehouse_id, current_user.company_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Almacén no encontrado")
    if payload.custom_data is not None:
        payload.custom_data = await validate_entity_custom_data(
            db, current_user.company_id, "delivery_goods", payload.custom_data, payload=payload
        )
    updated = await delivery_goods_crud.update(db, goods, payload)
    await run_workflows(
        db, company_id=current_user.company_id, entity_type="delivery_goods", event="actualizado", entity=updated
    )
    return updated


@router.post(
    "/movements", response_model=DeliveryGoodsMovementOut, status_code=status.HTTP_201_CREATED
)
async def create_delivery_goods_movement(
    payload: DeliveryGoodsMovementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("delivery", "write")),
) -> DeliveryGoodsMovementOut:
    goods = await delivery_goods_crud.get(db, payload.goods_id, current_user.company_id)
    if goods is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mercancía no encontrada")

    try:
        return await apply_movement(
            db,
            goods,
            movement_type=payload.movement_type,
            quantity=payload.quantity,
            unit_cost=payload.unit_cost,
            reference_doc=payload.reference_doc,
            notes=payload.notes,
            recorded_by=current_user.id,
        )
    except InvalidDeliveryGoodsMovement as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
