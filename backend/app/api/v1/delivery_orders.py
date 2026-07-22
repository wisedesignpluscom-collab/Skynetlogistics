import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.custom_fields import validate_entity_custom_data
from app.core.deps import get_current_driver, get_current_user, require_permission
from app.crud import client as client_crud
from app.crud import delivery_goods as delivery_goods_crud
from app.crud import delivery_order as delivery_order_crud
from app.crud import trip as trip_crud
from app.models.driver import Driver
from app.models.user import User
from app.schemas.common import Page
from app.schemas.delivery_order import (
    DeliveryOrderAssign,
    DeliveryOrderCreate,
    DeliveryOrderDeliver,
    DeliveryOrderFail,
    DeliveryOrderOut,
    DeliveryOrderUpdate,
)
from app.services import delivery_dispatch
from app.services.delivery_dispatch import InvalidDeliveryTransition
from app.utils.permissions import has_permission
from app.services.workflows import run_workflows

router = APIRouter(prefix="/delivery-orders", tags=["delivery"])


async def _own_driver(db: AsyncSession, user: User) -> Driver | None:
    result = await db.execute(select(Driver).where(Driver.user_id == user.id))
    return result.scalar_one_or_none()


def _require_dispatcher_write(user: User) -> None:
    if user.is_superadmin:
        return
    if not has_permission(user.role.permissions, "delivery", "write"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso 'write' sobre 'delivery'")


# ---------------------------------------------------------------------------
# Endpoints del conductor (aislamiento "solo lo propio" vía get_current_driver)
# ---------------------------------------------------------------------------
@router.get("/mine", response_model=list[DeliveryOrderOut])
async def list_my_delivery_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_driver: Driver = Depends(get_current_driver),
) -> list[DeliveryOrderOut]:
    trip_ids = await trip_crud.list_active_ids_for_driver(db, current_driver.id, current_user.company_id)
    return await delivery_order_crud.list_for_trips(db, trip_ids, current_user.company_id)


# ---------------------------------------------------------------------------
# Endpoints del despachador (require_permission delivery)
# ---------------------------------------------------------------------------
@router.get("", response_model=Page[DeliveryOrderOut])
async def list_delivery_orders(
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = None,
    trip_id: uuid.UUID | None = None,
    client_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("delivery", "read")),
) -> Page[DeliveryOrderOut]:
    items, total = await delivery_order_crud.list_paginated(
        db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        status=status_filter,
        trip_id=trip_id,
        client_id=client_id,
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=DeliveryOrderOut, status_code=status.HTTP_201_CREATED)
async def create_delivery_order(
    payload: DeliveryOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("delivery", "write")),
) -> DeliveryOrderOut:
    if await client_crud.get(db, payload.client_id, current_user.company_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
    for item in payload.items:
        if await delivery_goods_crud.get(db, item.goods_id, current_user.company_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Una de las mercancías no existe")
    payload.custom_data = await validate_entity_custom_data(
        db, current_user.company_id, "delivery_order", payload.custom_data, payload=payload
    )
    order = await delivery_order_crud.create(db, current_user.company_id, payload, current_user.id)
    await run_workflows(
        db, company_id=current_user.company_id, entity_type="delivery_order", event="creado", entity=order
    )
    return order


@router.get("/{order_id}", response_model=DeliveryOrderOut)
async def get_delivery_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("delivery", "read")),
) -> DeliveryOrderOut:
    order = await delivery_order_crud.get(db, order_id, current_user.company_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado")
    return order


@router.patch("/{order_id}", response_model=DeliveryOrderOut)
async def update_delivery_order(
    order_id: uuid.UUID,
    payload: DeliveryOrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("delivery", "write")),
) -> DeliveryOrderOut:
    order = await delivery_order_crud.get(db, order_id, current_user.company_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado")
    if order.status != "pendiente":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Solo se puede editar un pedido pendiente")
    if payload.custom_data is not None:
        payload.custom_data = await validate_entity_custom_data(
            db, current_user.company_id, "delivery_order", payload.custom_data, payload=payload
        )
    updated = await delivery_order_crud.update(db, order, payload)
    await run_workflows(
        db, company_id=current_user.company_id, entity_type="delivery_order", event="actualizado", entity=updated
    )
    return updated


@router.post("/{order_id}/assign", response_model=DeliveryOrderOut)
async def assign_delivery_order(
    order_id: uuid.UUID,
    payload: DeliveryOrderAssign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("delivery", "write")),
) -> DeliveryOrderOut:
    order = await delivery_order_crud.get(db, order_id, current_user.company_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado")
    trip = await trip_crud.get(db, payload.trip_id, current_user.company_id)
    if trip is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Viaje no encontrado")
    try:
        return await delivery_dispatch.assign_to_trip(db, order, trip, recorded_by=current_user.id)
    except InvalidDeliveryTransition as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


@router.post("/{order_id}/in-route", response_model=DeliveryOrderOut)
async def mark_delivery_order_in_route(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("delivery", "write")),
) -> DeliveryOrderOut:
    order = await delivery_order_crud.get(db, order_id, current_user.company_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado")
    try:
        return await delivery_dispatch.mark_in_route(db, order)
    except InvalidDeliveryTransition as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


# ---------------------------------------------------------------------------
# Entrega/fallo: los usa TANTO el despachador COMO el conductor. El actor se resuelve dentro:
# si el usuario tiene un Driver vinculado, valida que el pedido esté en uno de sus trips; si no,
# exige permiso 'delivery' 'write' (despachador). Mismo patrón que el chat de Fase 8.
# ---------------------------------------------------------------------------
async def _load_order_for_actor(db: AsyncSession, order_id: uuid.UUID, current_user: User):
    order = await delivery_order_crud.get(db, order_id, current_user.company_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido no encontrado")

    driver = await _own_driver(db, current_user)
    if driver is not None:
        active_trip_ids = await trip_crud.list_active_ids_for_driver(db, driver.id, current_user.company_id)
        if order.trip_id not in active_trip_ids:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Este pedido no está en uno de tus viajes")
    else:
        _require_dispatcher_write(current_user)
    return order


@router.post("/{order_id}/deliver", response_model=DeliveryOrderOut)
async def deliver_delivery_order(
    order_id: uuid.UUID,
    payload: DeliveryOrderDeliver,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DeliveryOrderOut:
    order = await _load_order_for_actor(db, order_id, current_user)
    try:
        return await delivery_dispatch.mark_delivered(
            db,
            order,
            delivered_by=current_user.id,
            delivery_proof_url=payload.delivery_proof_url,
            notes=payload.notes,
        )
    except InvalidDeliveryTransition as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


@router.post("/{order_id}/fail", response_model=DeliveryOrderOut)
async def fail_delivery_order(
    order_id: uuid.UUID,
    payload: DeliveryOrderFail,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DeliveryOrderOut:
    order = await _load_order_for_actor(db, order_id, current_user)
    try:
        return await delivery_dispatch.mark_failed(
            db,
            order,
            failure_reason=payload.failure_reason,
            return_stock=payload.return_stock,
            recorded_by=current_user.id,
        )
    except InvalidDeliveryTransition as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
