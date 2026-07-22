"""Motor de alertas: revisa mantenimientos próximos a vencer y licencias por expirar.

Se ejecuta una vez al día vía APScheduler (ver `app/main.py`). La función principal
`run_alert_checks` es pura respecto a la sesión de DB que recibe, por lo que se puede
invocar directamente desde tests sin levantar el scheduler.
"""

import uuid
from datetime import date, timezone, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tire_settings as tire_settings_crud
from app.crud.alert import create_if_not_exists
from app.models.delivery_goods import DeliveryGoods
from app.models.driver import Driver
from app.models.driver_document import DriverDocument
from app.models.driver_document_type import DriverDocumentType
from app.models.incident_report import IncidentReport
from app.models.inventory_item import InventoryItem
from app.models.maintenance_task import MaintenanceTask
from app.models.tire import Tire
from app.models.vehicle import Vehicle
from app.models.vehicle_document import VehicleDocument
from app.models.vehicle_document_type import VehicleDocumentType

# Umbrales por defecto (días u odómetro restante) para disparar cada nivel de severidad.
MAINTENANCE_DATE_MEDIUM_DAYS = 7
MAINTENANCE_DATE_HIGH_DAYS = 2
MAINTENANCE_KM_MEDIUM = 500
MAINTENANCE_KM_HIGH = 100
LICENSE_MEDIUM_DAYS = 30
LICENSE_HIGH_DAYS = 7

ACTIVE_TASK_STATUSES = ("pendiente", "en_proceso")


def _severity_from_remaining(remaining: int, high_threshold: int, medium_threshold: int) -> str | None:
    if remaining <= high_threshold:
        return "alta"
    if remaining <= medium_threshold:
        return "media"
    return None


async def _check_maintenance_tasks(
    db: AsyncSession, today: date, vehicle_ids: list[uuid.UUID] | None = None
) -> int:
    query = (
        select(MaintenanceTask, Vehicle)
        .join(Vehicle, Vehicle.id == MaintenanceTask.vehicle_id)
        .where(MaintenanceTask.status.in_(ACTIVE_TASK_STATUSES))
    )
    if vehicle_ids is not None:
        query = query.where(MaintenanceTask.vehicle_id.in_(vehicle_ids))
    result = await db.execute(query)
    created = 0
    for task, vehicle in result.all():
        severity: str | None = None
        remaining_desc = ""

        if task.scheduled_by == "tiempo" and task.due_date is not None:
            days_left = (task.due_date - today).days
            severity = _severity_from_remaining(
                days_left, MAINTENANCE_DATE_HIGH_DAYS, MAINTENANCE_DATE_MEDIUM_DAYS
            )
            remaining_desc = f"en {days_left} día(s)" if days_left >= 0 else f"vencido hace {-days_left} día(s)"
        elif task.scheduled_by == "km" and task.due_km is not None:
            km_left = task.due_km - vehicle.current_odometer_km
            severity = _severity_from_remaining(
                km_left, MAINTENANCE_KM_HIGH, MAINTENANCE_KM_MEDIUM
            )
            remaining_desc = f"en {km_left} km" if km_left >= 0 else f"superado por {-km_left} km"

        if severity is None:
            continue

        message = f"Mantenimiento {task.type} de {vehicle.plate} vence {remaining_desc}"
        inserted = await create_if_not_exists(
            db,
            company_id=task.company_id,
            type="maintenance_due",
            entity_type="maintenance_task",
            entity_id=task.id,
            message=message,
            severity=severity,
        )
        if inserted:
            created += 1
    return created


async def _check_driver_licenses(db: AsyncSession, today: date) -> int:
    result = await db.execute(select(Driver).where(Driver.status == "activo"))
    created = 0
    for driver in result.scalars().all():
        days_left = (driver.license_expiry - today).days
        severity = _severity_from_remaining(days_left, LICENSE_HIGH_DAYS, LICENSE_MEDIUM_DAYS)
        if severity is None:
            continue

        remaining_desc = f"en {days_left} día(s)" if days_left >= 0 else f"vencida hace {-days_left} día(s)"
        message = f"Licencia de {driver.name} vence {remaining_desc}"
        inserted = await create_if_not_exists(
            db,
            company_id=driver.company_id,
            type="license_expiring",
            entity_type="driver",
            entity_id=driver.id,
            message=message,
            severity=severity,
        )
        if inserted:
            created += 1
    return created


async def _check_driver_documents(db: AsyncSession, today: date, driver_ids: list[uuid.UUID] | None = None) -> int:
    """Revisa `driver_documents.expiry_date` contra el `alert_days_before` configurable de cada
    `driver_document_types` (mismo patrón que `tire_settings`/`disparity_threshold_mm`, pero el
    umbral vive por tipo de documento en vez de por empresa). Solo genera una severidad ("alta")
    a diferencia del resto de chequeos, que no distinguen niveles intermedios; el detalle de
    urgencia real ya está en el mensaje ("vence en N días" / "vencido hace N días")."""
    query = (
        select(DriverDocument, DriverDocumentType, Driver)
        .join(DriverDocumentType, DriverDocumentType.id == DriverDocument.document_type_id)
        .join(Driver, Driver.id == DriverDocument.driver_id)
        .where(DriverDocument.expiry_date.is_not(None), Driver.status == "activo")
    )
    if driver_ids is not None:
        query = query.where(DriverDocument.driver_id.in_(driver_ids))
    result = await db.execute(query)

    created = 0
    for document, doc_type, driver in result.all():
        days_left = (document.expiry_date - today).days
        if days_left > doc_type.alert_days_before:
            continue

        remaining_desc = f"en {days_left} día(s)" if days_left >= 0 else f"vencido hace {-days_left} día(s)"
        message = f"{doc_type.name} de {driver.name} vence {remaining_desc}"
        inserted = await create_if_not_exists(
            db,
            company_id=document.company_id,
            type="driver_document_expiring",
            entity_type="driver_document",
            entity_id=document.id,
            message=message,
            severity="alta" if days_left <= 7 else "media",
        )
        if inserted:
            created += 1
    return created


async def _check_vehicle_documents(
    db: AsyncSession, today: date, vehicle_ids: list[uuid.UUID] | None = None
) -> int:
    """Mismo patrón que `_check_driver_documents`, pero scoped por `vehicle_ids` (como
    mantenimiento y disparidad de neumáticos) en vez de por `driver_ids`, ya que los documentos
    de vehículo se revalidan junto con el resto de chequeos scoped a un vehículo."""
    query = (
        select(VehicleDocument, VehicleDocumentType, Vehicle)
        .join(VehicleDocumentType, VehicleDocumentType.id == VehicleDocument.document_type_id)
        .join(Vehicle, Vehicle.id == VehicleDocument.vehicle_id)
        .where(VehicleDocument.expiry_date.is_not(None))
    )
    if vehicle_ids is not None:
        query = query.where(VehicleDocument.vehicle_id.in_(vehicle_ids))
    result = await db.execute(query)

    created = 0
    for document, doc_type, vehicle in result.all():
        days_left = (document.expiry_date - today).days
        if days_left > doc_type.alert_days_before:
            continue

        remaining_desc = f"en {days_left} día(s)" if days_left >= 0 else f"vencido hace {-days_left} día(s)"
        message = f"{doc_type.name} de {vehicle.plate} vence {remaining_desc}"
        inserted = await create_if_not_exists(
            db,
            company_id=document.company_id,
            type="vehicle_document_expiring",
            entity_type="vehicle_document",
            entity_id=document.id,
            message=message,
            severity="alta" if days_left <= 7 else "media",
        )
        if inserted:
            created += 1
    return created


async def _check_tire_disparity(db: AsyncSession, vehicle_ids: list[uuid.UUID] | None = None) -> int:
    """Agrupa neumáticos instalados por (vehicle_id, axle_number, axle_side) — la posición
    "morocha" — y genera una alerta cuando la diferencia de espesor entre el par supera el
    umbral configurable de la empresa (`tire_settings`).
    """
    query = select(Tire).where(Tire.status == "instalado")
    if vehicle_ids is not None:
        query = query.where(Tire.vehicle_id.in_(vehicle_ids))
    result = await db.execute(query)

    groups: dict[tuple[uuid.UUID, int, str], list[Tire]] = {}
    for tire in result.scalars().all():
        if tire.vehicle_id is None or tire.axle_number is None or tire.axle_side is None:
            continue
        key = (tire.vehicle_id, tire.axle_number, tire.axle_side)
        groups.setdefault(key, []).append(tire)

    threshold_cache: dict[uuid.UUID, float] = {}
    created = 0
    for (vehicle_id, axle_number, axle_side), group_tires in groups.items():
        if len(group_tires) != 2:
            continue
        tire_a, tire_b = group_tires
        company_id = tire_a.company_id
        if company_id not in threshold_cache:
            settings = await tire_settings_crud.get_or_create(db, company_id)
            threshold_cache[company_id] = float(settings.disparity_threshold_mm)

        diff = abs(float(tire_a.current_thickness_mm) - float(tire_b.current_thickness_mm))
        if diff <= threshold_cache[company_id]:
            continue

        low_tire = tire_a if tire_a.current_thickness_mm < tire_b.current_thickness_mm else tire_b
        message = (
            f"Disparidad de espesor en eje {axle_number} ({axle_side}): "
            f"{tire_a.unique_code} {tire_a.current_thickness_mm}mm vs "
            f"{tire_b.unique_code} {tire_b.current_thickness_mm}mm"
        )
        inserted = await create_if_not_exists(
            db,
            company_id=company_id,
            type="tire_disparity",
            entity_type="tire",
            entity_id=low_tire.id,
            message=message,
            severity="media",
        )
        if inserted:
            created += 1
    return created


async def _check_low_stock(db: AsyncSession, item_ids: list[uuid.UUID] | None = None) -> int:
    """Genera una alerta cuando `inventory_items.quantity` cae a o por debajo de `min_stock`."""
    query = select(InventoryItem).where(InventoryItem.quantity <= InventoryItem.min_stock)
    if item_ids is not None:
        query = query.where(InventoryItem.id.in_(item_ids))
    result = await db.execute(query)

    created = 0
    for item in result.scalars().all():
        message = f"Stock bajo de {item.name} ({item.sku}): {item.quantity} {item.unit} (mínimo {item.min_stock})"
        inserted = await create_if_not_exists(
            db,
            company_id=item.company_id,
            type="low_stock",
            entity_type="inventory_item",
            entity_id=item.id,
            message=message,
            severity="media",
        )
        if inserted:
            created += 1
    return created


# `alerts.severity` solo tiene 3 niveles (baja/media/alta); incident_reports tiene 4
# (baja/media/alta/critica) — mismo desajuste documentado para fatiga (ver RISK_LEVEL_TO_SEVERITY
# en app/jobs/fatigue.py), "critica" cae en "alta" de alerts.
INCIDENT_SEVERITY_TO_ALERT_SEVERITY = {"alta": "alta", "critica": "alta"}


async def create_incident_alert(db: AsyncSession, incident: IncidentReport) -> bool:
    """Genera una alerta para un `incident_report` recién creado con severidad alta/crítica.

    A diferencia del resto de chequeos de este módulo, no corre en el barrido diario — se llama
    directo desde `POST /incident-reports` (Fase 8) al momento de crear el reporte, reutilizando
    `create_if_not_exists` para el mismo anti-duplicado (aquí no debería duplicarse nunca porque
    cada `incident_report.id` es único, pero se mantiene el mismo patrón por consistencia).
    """
    alert_severity = INCIDENT_SEVERITY_TO_ALERT_SEVERITY.get(incident.severity)
    if alert_severity is None:
        return False
    return await create_if_not_exists(
        db,
        company_id=incident.company_id,
        type="incident_report",
        entity_type="incident_report",
        entity_id=incident.id,
        message=f"Reporte de incidencia ({incident.type}) — {incident.description[:120]}",
        severity=alert_severity,
    )


async def _check_low_stock_delivery(db: AsyncSession, goods_ids: list[uuid.UUID] | None = None) -> int:
    """Mismo patrón que `_check_low_stock` (Fase 6) pero sobre `delivery_goods` (Fase 9A):
    alerta `low_stock_delivery` cuando `quantity <= min_stock`."""
    query = select(DeliveryGoods).where(DeliveryGoods.quantity <= DeliveryGoods.min_stock)
    if goods_ids is not None:
        query = query.where(DeliveryGoods.id.in_(goods_ids))
    result = await db.execute(query)

    created = 0
    for goods in result.scalars().all():
        message = (
            f"Stock bajo de mercancía {goods.name} ({goods.sku}): "
            f"{goods.quantity} {goods.unit} (mínimo {goods.min_stock})"
        )
        inserted = await create_if_not_exists(
            db,
            company_id=goods.company_id,
            type="low_stock_delivery",
            entity_type="delivery_goods",
            entity_id=goods.id,
            message=message,
            severity="media",
        )
        if inserted:
            created += 1
    return created


async def run_alert_checks(
    db: AsyncSession,
    *,
    today: date | None = None,
    vehicle_ids: list[uuid.UUID] | None = None,
    item_ids: list[uuid.UUID] | None = None,
    driver_ids: list[uuid.UUID] | None = None,
    goods_ids: list[uuid.UUID] | None = None,
) -> dict[str, int]:
    """Ejecuta los chequeos y devuelve cuántas alertas nuevas se crearon de cada tipo.

    Por defecto (todos los `*_ids=None`) revisa todos los vehículos, conductores e ítems de
    inventario de todas las empresas — es el comportamiento del job diario programado.
    Si se pasa `vehicle_ids`, solo revisa mantenimiento, disparidad de neumáticos y documentos por
    vencer de esos vehículos (uso: revalidar tras actualizar el odómetro al cerrar un viaje en
    Fase 2, tras un movimiento de neumático en Fase 5, o tras crear/editar un documento de
    vehículo). Si se pasa `item_ids`, solo revisa stock bajo de esos ítems (uso: revalidar tras un
    movimiento de inventario en Fase 6). Si se pasa `driver_ids`, solo revisa documentos por
    vencer de esos conductores (uso: revalidar tras crear/editar un documento). Todos los
    parámetros de scoping son independientes — mismo patrón "extender con parámetro opcional" que
    el resto de fases, sin reimplementar la lógica de umbrales/severidad/anti-duplicados.
    """
    effective_today = today or datetime.now(timezone.utc).date()
    empty = {
        "maintenance_due": 0,
        "license_expiring": 0,
        "tire_disparity": 0,
        "low_stock": 0,
        "low_stock_delivery": 0,
        "driver_document_expiring": 0,
        "vehicle_document_expiring": 0,
    }

    if item_ids is not None:
        return {**empty, "low_stock": await _check_low_stock(db, item_ids)}

    if goods_ids is not None:
        return {**empty, "low_stock_delivery": await _check_low_stock_delivery(db, goods_ids)}

    if driver_ids is not None:
        return {
            **empty,
            "driver_document_expiring": await _check_driver_documents(db, effective_today, driver_ids),
        }

    maintenance_created = await _check_maintenance_tasks(db, effective_today, vehicle_ids)
    tire_disparity_created = await _check_tire_disparity(db, vehicle_ids)
    vehicle_document_created = await _check_vehicle_documents(db, effective_today, vehicle_ids)
    if vehicle_ids is not None:
        return {
            **empty,
            "maintenance_due": maintenance_created,
            "tire_disparity": tire_disparity_created,
            "vehicle_document_expiring": vehicle_document_created,
        }
    license_created = await _check_driver_licenses(db, effective_today)
    low_stock_created = await _check_low_stock(db)
    low_stock_delivery_created = await _check_low_stock_delivery(db)
    document_created = await _check_driver_documents(db, effective_today)
    return {
        "maintenance_due": maintenance_created,
        "license_expiring": license_created,
        "low_stock": low_stock_created,
        "low_stock_delivery": low_stock_delivery_created,
        "tire_disparity": tire_disparity_created,
        "driver_document_expiring": document_created,
        "vehicle_document_expiring": vehicle_document_created,
    }
