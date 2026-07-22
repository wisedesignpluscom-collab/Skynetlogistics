"""Transición atómica de stock de un ítem de inventario.

Cada movimiento (entrada, salida, ajuste) actualiza `inventory_items.quantity` y crea el
registro histórico en `inventory_movements` en un solo lugar — mismo patrón que
`services/tire_movements.py::apply_movement` (Fase 5) y `services/vehicle_odometer.py::
advance_odometer`: el invariante "quantity nunca queda negativa" se garantiza en un solo sitio.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import inventory_movement as inventory_movement_crud
from app.crud import provider as provider_crud
from app.crud import vehicle as vehicle_crud
from app.jobs.alerts import run_alert_checks
from app.models.inventory_item import InventoryItem
from app.models.inventory_movement import InventoryMovement


class InvalidInventoryMovement(ValueError):
    pass


async def apply_movement(
    db: AsyncSession,
    item: InventoryItem,
    *,
    movement_type: str,
    quantity: float,
    vehicle_id: uuid.UUID | None = None,
    provider_id: uuid.UUID | None = None,
    unit_cost: float | None = None,
    invoice_number: str | None = None,
    tax_percentage: float | None = None,
    reference_doc: str | None = None,
    notes: str | None = None,
    recorded_by: uuid.UUID | None = None,
) -> InventoryMovement:
    if movement_type not in ("entrada", "salida", "ajuste"):
        raise InvalidInventoryMovement(f"Tipo de movimiento desconocido: {movement_type}")
    if quantity == 0:
        raise InvalidInventoryMovement("La cantidad del movimiento no puede ser cero")
    if vehicle_id is not None and await vehicle_crud.get(db, vehicle_id, item.company_id) is None:
        raise InvalidInventoryMovement("Vehículo no encontrado")
    if provider_id is not None and await provider_crud.get(db, provider_id, item.company_id) is None:
        raise InvalidInventoryMovement("Proveedor no encontrado")

    if movement_type == "entrada":
        if quantity < 0:
            raise InvalidInventoryMovement("'entrada' requiere una cantidad positiva")
        delta = quantity
    elif movement_type == "salida":
        if quantity < 0:
            raise InvalidInventoryMovement("'salida' requiere una cantidad positiva")
        delta = -quantity
    else:  # ajuste: la cantidad es el delta explícito, puede ser positivo o negativo
        delta = quantity

    new_quantity = float(item.quantity) + delta
    if new_quantity < 0:
        raise InvalidInventoryMovement(
            f"El movimiento dejaría el stock en {new_quantity}, no puede quedar negativo"
        )

    item.quantity = new_quantity

    movement = await inventory_movement_crud.create(
        db,
        company_id=item.company_id,
        item_id=item.id,
        movement_type=movement_type,
        quantity=quantity,
        vehicle_id=vehicle_id,
        provider_id=provider_id,
        unit_cost=unit_cost,
        invoice_number=invoice_number,
        tax_percentage=tax_percentage,
        reference_doc=reference_doc,
        notes=notes,
        recorded_by=recorded_by,
    )

    await db.commit()
    await db.refresh(item)
    await db.refresh(movement)

    await run_alert_checks(db, item_ids=[item.id])

    return movement
