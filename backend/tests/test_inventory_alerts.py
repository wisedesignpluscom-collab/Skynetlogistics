from sqlalchemy import select

from app.jobs.alerts import run_alert_checks
from app.models.alert import Alert
from app.models.inventory_item import InventoryItem
from app.services.inventory_movements import apply_movement


async def test_daily_sweep_creates_low_stock_alert(db, company, warehouse) -> None:
    item = InventoryItem(
        company_id=company.id,
        warehouse_id=warehouse.id,
        sku="SKU-LOW",
        name="Pastillas de freno",
        unit="juego",
        quantity=2,
        min_stock=5,
        unit_cost=20,
    )
    db.add(item)
    await db.commit()

    result = await run_alert_checks(db)
    assert result["low_stock"] == 1

    alert = (await db.execute(select(Alert).where(Alert.type == "low_stock"))).scalar_one()
    assert alert.entity_id == item.id
    assert alert.severity == "media"


async def test_sweep_ignores_items_above_min_stock(db, company, warehouse) -> None:
    item = InventoryItem(
        company_id=company.id,
        warehouse_id=warehouse.id,
        sku="SKU-OK",
        name="Bujías",
        unit="unidad",
        quantity=50,
        min_stock=5,
        unit_cost=3,
    )
    db.add(item)
    await db.commit()

    result = await run_alert_checks(db)
    assert result["low_stock"] == 0


async def test_movement_triggers_scoped_low_stock_check(db, company, warehouse) -> None:
    item = InventoryItem(
        company_id=company.id,
        warehouse_id=warehouse.id,
        sku="SKU-SCOPED",
        name="Correas",
        unit="unidad",
        quantity=10,
        min_stock=5,
        unit_cost=8,
    )
    db.add(item)
    await db.flush()

    # una salida que deja el stock en 3 (<= min_stock 5) debe disparar la alerta sin esperar
    # al barrido diario, igual que la disparidad de neumáticos en Fase 5.
    await apply_movement(db, item, movement_type="salida", quantity=7)

    alert = (await db.execute(select(Alert).where(Alert.type == "low_stock"))).scalar_one()
    assert alert.entity_id == item.id


async def test_alert_deduped_on_repeated_sweep(db, company, warehouse) -> None:
    item = InventoryItem(
        company_id=company.id,
        warehouse_id=warehouse.id,
        sku="SKU-DEDUPE",
        name="Filtros",
        unit="unidad",
        quantity=1,
        min_stock=5,
        unit_cost=4,
    )
    db.add(item)
    await db.commit()

    first = await run_alert_checks(db)
    second = await run_alert_checks(db)
    assert first["low_stock"] == 1
    assert second["low_stock"] == 0

    alerts = (await db.execute(select(Alert).where(Alert.type == "low_stock"))).scalars().all()
    assert len(alerts) == 1
