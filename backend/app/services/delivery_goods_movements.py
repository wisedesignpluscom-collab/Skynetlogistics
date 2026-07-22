"""Transición atómica de stock de la mercancía de reparto (Fase 9A).

Mismo patrón que `services/inventory_movements.py::apply_movement` (Fase 6): entrada/salida/ajuste
actualizan `delivery_goods.quantity` y crean el registro histórico en un solo lugar, garantizando
que `quantity` nunca quede negativa. En Fase 9C el despacho de un pedido reusará esta misma función
para descontar stock.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import delivery_goods as delivery_goods_crud
from app.jobs.alerts import run_alert_checks
from app.models.delivery_goods import DeliveryGoods, DeliveryGoodsMovement


class InvalidDeliveryGoodsMovement(ValueError):
    pass


async def apply_movement(
    db: AsyncSession,
    goods: DeliveryGoods,
    *,
    movement_type: str,
    quantity: float,
    unit_cost: float | None = None,
    reference_doc: str | None = None,
    notes: str | None = None,
    recorded_by: uuid.UUID | None = None,
) -> DeliveryGoodsMovement:
    if movement_type not in ("entrada", "salida", "ajuste"):
        raise InvalidDeliveryGoodsMovement(f"Tipo de movimiento desconocido: {movement_type}")
    if quantity == 0:
        raise InvalidDeliveryGoodsMovement("La cantidad del movimiento no puede ser cero")

    if movement_type == "entrada":
        if quantity < 0:
            raise InvalidDeliveryGoodsMovement("'entrada' requiere una cantidad positiva")
        delta = quantity
    elif movement_type == "salida":
        if quantity < 0:
            raise InvalidDeliveryGoodsMovement("'salida' requiere una cantidad positiva")
        delta = -quantity
    else:  # ajuste: la cantidad es el delta explícito, puede ser positivo o negativo
        delta = quantity

    new_quantity = float(goods.quantity) + delta
    if new_quantity < 0:
        raise InvalidDeliveryGoodsMovement(
            f"El movimiento dejaría el stock en {new_quantity}, no puede quedar negativo"
        )

    goods.quantity = new_quantity

    movement = await delivery_goods_crud.create_movement(
        db,
        company_id=goods.company_id,
        goods_id=goods.id,
        movement_type=movement_type,
        quantity=quantity,
        unit_cost=unit_cost,
        reference_doc=reference_doc,
        notes=notes,
        recorded_by=recorded_by,
    )

    await db.commit()
    await db.refresh(goods)
    await db.refresh(movement)

    await run_alert_checks(db, goods_ids=[goods.id])

    return movement
