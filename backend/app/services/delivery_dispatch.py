"""Transiciones de estado de un pedido de reparto (Fase 9B).

Centraliza el ciclo de vida del pedido y el efecto sobre el stock de mercancía:
- `assign_to_trip`: pendiente -> asignado. Descuenta stock (salida) de cada línea vía
  `delivery_goods_movements.apply_movement` (Fase 9A). Es el "despacho": la mercancía sale a la
  calle. En 9C el confirm del VRP reutiliza esta misma función.
- `mark_in_route` / `mark_delivered` / `mark_failed`: avanzan el estado. `mark_failed` con
  `return_stock=True` reingresa la mercancía (entrada) porque no se entregó.

Mismo criterio que `services/vrp_planning.py` / `services/tire_movements.py`: un único punto para
la lógica de negocio, para que endpoint del despachador y endpoint del conductor (y el VRP en 9C)
compartan exactamente el mismo comportamiento.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import delivery_goods as delivery_goods_crud
from app.models.delivery_order import DeliveryOrder
from app.models.trip import Trip
from app.services.delivery_goods_movements import InvalidDeliveryGoodsMovement, apply_movement


class InvalidDeliveryTransition(ValueError):
    pass


async def _aggregate_demand(order: DeliveryOrder) -> dict[uuid.UUID, float]:
    """Suma la cantidad requerida por goods_id (por si el pedido tiene dos líneas del mismo SKU)."""
    demand: dict[uuid.UUID, float] = {}
    for item in order.items:
        demand[item.goods_id] = demand.get(item.goods_id, 0.0) + float(item.quantity)
    return demand


async def assign_to_trip(
    db: AsyncSession, order: DeliveryOrder, trip: Trip, *, recorded_by: uuid.UUID | None
) -> DeliveryOrder:
    if order.status != "pendiente":
        raise InvalidDeliveryTransition("Solo se puede asignar un pedido en estado 'pendiente'")

    demand = await _aggregate_demand(order)

    # Valida stock suficiente de TODAS las líneas antes de descontar cualquiera (evita descuentos
    # parciales si una línea no alcanza).
    goods_by_id = {}
    for goods_id, qty in demand.items():
        goods = await delivery_goods_crud.get(db, goods_id, order.company_id)
        if goods is None:
            raise InvalidDeliveryTransition("Una de las mercancías del pedido no existe")
        if float(goods.quantity) < qty:
            raise InvalidDeliveryTransition(
                f"Stock insuficiente de {goods.name}: hay {goods.quantity}, se requieren {qty}"
            )
        goods_by_id[goods_id] = goods

    for goods_id, qty in demand.items():
        try:
            await apply_movement(
                db,
                goods_by_id[goods_id],
                movement_type="salida",
                quantity=qty,
                reference_doc=f"Despacho pedido {order.id}",
                recorded_by=recorded_by,
            )
        except InvalidDeliveryGoodsMovement as exc:  # pragma: no cover - ya validado arriba
            raise InvalidDeliveryTransition(str(exc)) from exc

    order.trip_id = trip.id
    order.status = "asignado"
    await db.commit()
    await db.refresh(order)
    return order


async def mark_in_route(db: AsyncSession, order: DeliveryOrder) -> DeliveryOrder:
    if order.status != "asignado":
        raise InvalidDeliveryTransition("Solo un pedido 'asignado' puede pasar a 'en_ruta'")
    order.status = "en_ruta"
    await db.commit()
    await db.refresh(order)
    return order


async def mark_delivered(
    db: AsyncSession,
    order: DeliveryOrder,
    *,
    delivered_by: uuid.UUID | None,
    delivery_proof_url: str | None,
    notes: str | None,
) -> DeliveryOrder:
    if order.status not in ("asignado", "en_ruta"):
        raise InvalidDeliveryTransition("Solo un pedido asignado o en ruta puede marcarse entregado")
    from datetime import datetime, timezone

    order.status = "entregado"
    order.delivered_at = datetime.now(timezone.utc)
    order.delivered_by = delivered_by
    if delivery_proof_url is not None:
        order.delivery_proof_url = delivery_proof_url
    if notes is not None:
        order.notes = notes
    await db.commit()
    await db.refresh(order)
    return order


async def mark_failed(
    db: AsyncSession,
    order: DeliveryOrder,
    *,
    failure_reason: str,
    return_stock: bool,
    recorded_by: uuid.UUID | None,
) -> DeliveryOrder:
    if order.status not in ("asignado", "en_ruta"):
        raise InvalidDeliveryTransition("Solo un pedido asignado o en ruta puede marcarse fallido")

    if return_stock:
        demand = await _aggregate_demand(order)
        for goods_id, qty in demand.items():
            goods = await delivery_goods_crud.get(db, goods_id, order.company_id)
            if goods is not None:
                await apply_movement(
                    db,
                    goods,
                    movement_type="entrada",
                    quantity=qty,
                    reference_doc=f"Retorno pedido fallido {order.id}",
                    recorded_by=recorded_by,
                )

    order.status = "fallido"
    order.failure_reason = failure_reason
    await db.commit()
    await db.refresh(order)
    return order
