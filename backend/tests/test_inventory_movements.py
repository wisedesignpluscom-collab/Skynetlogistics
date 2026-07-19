import pytest

from app.models.inventory_item import InventoryItem
from app.services.inventory_movements import InvalidInventoryMovement, apply_movement


def _make_item(company, warehouse, *, quantity: float = 10, min_stock: float = 0) -> InventoryItem:
    return InventoryItem(
        company_id=company.id,
        warehouse_id=warehouse.id,
        sku="SKU-001",
        name="Filtro de aceite",
        unit="unidad",
        quantity=quantity,
        min_stock=min_stock,
        unit_cost=5,
    )


async def test_entrada_increases_quantity(db, company, warehouse) -> None:
    item = _make_item(company, warehouse, quantity=10)
    db.add(item)
    await db.flush()

    movement = await apply_movement(db, item, movement_type="entrada", quantity=5, unit_cost=6)
    assert movement.movement_type == "entrada"
    assert float(item.quantity) == 15


async def test_salida_decreases_quantity(db, company, warehouse) -> None:
    item = _make_item(company, warehouse, quantity=10)
    db.add(item)
    await db.flush()

    await apply_movement(db, item, movement_type="salida", quantity=4)
    assert float(item.quantity) == 6


async def test_salida_cannot_go_negative(db, company, warehouse) -> None:
    item = _make_item(company, warehouse, quantity=3)
    db.add(item)
    await db.flush()

    with pytest.raises(InvalidInventoryMovement):
        await apply_movement(db, item, movement_type="salida", quantity=5)
    assert float(item.quantity) == 3


async def test_ajuste_applies_signed_delta(db, company, warehouse) -> None:
    item = _make_item(company, warehouse, quantity=10)
    db.add(item)
    await db.flush()

    await apply_movement(db, item, movement_type="ajuste", quantity=-3)
    assert float(item.quantity) == 7

    await apply_movement(db, item, movement_type="ajuste", quantity=2)
    assert float(item.quantity) == 9


async def test_ajuste_cannot_leave_negative_stock(db, company, warehouse) -> None:
    item = _make_item(company, warehouse, quantity=2)
    db.add(item)
    await db.flush()

    with pytest.raises(InvalidInventoryMovement):
        await apply_movement(db, item, movement_type="ajuste", quantity=-5)
    assert float(item.quantity) == 2


async def test_zero_quantity_rejected(db, company, warehouse) -> None:
    item = _make_item(company, warehouse, quantity=5)
    db.add(item)
    await db.flush()

    with pytest.raises(InvalidInventoryMovement):
        await apply_movement(db, item, movement_type="entrada", quantity=0)


async def test_entrada_with_negative_quantity_rejected(db, company, warehouse) -> None:
    item = _make_item(company, warehouse, quantity=5)
    db.add(item)
    await db.flush()

    with pytest.raises(InvalidInventoryMovement):
        await apply_movement(db, item, movement_type="entrada", quantity=-5)


async def test_movement_creates_history_record(db, company, warehouse) -> None:
    item = _make_item(company, warehouse, quantity=10)
    db.add(item)
    await db.flush()

    movement = await apply_movement(
        db, item, movement_type="entrada", quantity=5, reference_doc="FAC-001", notes="Compra inicial"
    )
    assert movement.item_id == item.id
    assert movement.reference_doc == "FAC-001"
    assert movement.notes == "Compra inicial"
