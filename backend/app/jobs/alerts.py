"""Motor de alertas: revisa mantenimientos próximos a vencer y licencias por expirar.

Se ejecuta una vez al día vía APScheduler (ver `app/main.py`). La función principal
`run_alert_checks` es pura respecto a la sesión de DB que recibe, por lo que se puede
invocar directamente desde tests sin levantar el scheduler.
"""

import uuid
from datetime import date, timezone, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.alert import create_if_not_exists
from app.models.driver import Driver
from app.models.maintenance_task import MaintenanceTask
from app.models.vehicle import Vehicle

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


async def run_alert_checks(
    db: AsyncSession, *, today: date | None = None, vehicle_ids: list[uuid.UUID] | None = None
) -> dict[str, int]:
    """Ejecuta los chequeos y devuelve cuántas alertas nuevas se crearon de cada tipo.

    Por defecto (`vehicle_ids=None`) revisa todos los vehículos y conductores de todas las
    empresas — es el comportamiento del job diario programado. Si se pasa `vehicle_ids`, solo
    revisa mantenimiento de esos vehículos (uso: revalidar tras actualizar el odómetro al cerrar
    un viaje en Fase 2, sin reimplementar la lógica de umbrales/severidad/anti-duplicados). En ese
    caso se omite el chequeo de licencias, que no depende del odómetro del vehículo.
    """
    effective_today = today or datetime.now(timezone.utc).date()
    maintenance_created = await _check_maintenance_tasks(db, effective_today, vehicle_ids)
    if vehicle_ids is not None:
        return {"maintenance_due": maintenance_created, "license_expiring": 0}
    license_created = await _check_driver_licenses(db, effective_today)
    return {"maintenance_due": maintenance_created, "license_expiring": license_created}
