"""Transición atómica de estado de un neumático.

Cada movimiento (instalación, desinstalación, envío a reparación/reencauche, retorno de
taller) actualiza `tires` y crea el registro histórico en `tire_movements` en un solo lugar,
reutilizado tanto por el endpoint individual como por el de movimiento en lote — mismo patrón
que `services/vehicle_odometer.py::advance_odometer`. Así el invariante de estado (instalado
siempre con vehicle_id+posición, almacén siempre con warehouse_id, nunca ambos) se garantiza
en un solo sitio.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tire as tire_crud
from app.crud import tire_movement as tire_movement_crud
from app.crud import vehicle as vehicle_crud
from app.jobs.alerts import run_alert_checks
from app.models.tire import Tire
from app.models.tire_movement import TireMovement

SOURCE_STATUSES: dict[str, tuple[str, ...]] = {
    "instalacion": ("almacen",),
    "desinstalacion": ("instalado",),
    "envio_reparacion": ("instalado", "almacen"),
    "envio_reencauche": ("instalado", "almacen"),
    "retorno_taller": ("reparacion",),
}

TARGET_STATUS: dict[str, str] = {
    "instalacion": "instalado",
    "desinstalacion": "almacen",
    "envio_reparacion": "reparacion",
    "envio_reencauche": "reparacion",
    "retorno_taller": "almacen",
}


class InvalidTireMovement(ValueError):
    pass


async def apply_movement(
    db: AsyncSession,
    tire: Tire,
    *,
    movement_type: str,
    vehicle_id: uuid.UUID | None = None,
    axle_number: int | None = None,
    axle_side: str | None = None,
    axle_dual_position: str | None = None,
    warehouse_id: uuid.UUID | None = None,
    provider_id: uuid.UUID | None = None,
    thickness_mm: float | None = None,
    notes: str | None = None,
    recorded_by: uuid.UUID | None = None,
) -> TireMovement:
    if movement_type not in SOURCE_STATUSES:
        raise InvalidTireMovement(f"Tipo de movimiento desconocido: {movement_type}")
    if tire.status not in SOURCE_STATUSES[movement_type]:
        raise InvalidTireMovement(
            f"No se puede aplicar '{movement_type}' a un neumático en estado '{tire.status}'"
        )

    affected_vehicle_ids: set[uuid.UUID] = set()
    km_at_movement: int | None = None
    snapshot_vehicle_id = vehicle_id
    snapshot_axle_number = axle_number
    snapshot_axle_side = axle_side
    snapshot_axle_dual_position = axle_dual_position

    if movement_type == "instalacion":
        if None in (vehicle_id, axle_number, axle_side, axle_dual_position):
            raise InvalidTireMovement(
                "'instalacion' requiere vehicle_id, axle_number, axle_side y axle_dual_position"
            )
        vehicle = await vehicle_crud.get(db, vehicle_id, tire.company_id)
        if vehicle is None:
            raise InvalidTireMovement("Vehículo no encontrado")
        occupant = await tire_crud.get_installed_at_position(
            db,
            company_id=tire.company_id,
            vehicle_id=vehicle_id,
            axle_number=axle_number,
            axle_side=axle_side,
            axle_dual_position=axle_dual_position,
        )
        if occupant is not None and occupant.id != tire.id:
            raise InvalidTireMovement("Esa posición ya tiene un neumático instalado")

        km_at_movement = vehicle.current_odometer_km
        tire.vehicle_id = vehicle_id
        tire.axle_number = axle_number
        tire.axle_side = axle_side
        tire.axle_dual_position = axle_dual_position
        tire.warehouse_id = None
        affected_vehicle_ids.add(vehicle_id)

    elif movement_type == "desinstalacion":
        if warehouse_id is None:
            raise InvalidTireMovement("'desinstalacion' requiere warehouse_id")
        km_at_movement, snapshot_vehicle_id = await _read_current_position_km(db, tire)
        if snapshot_vehicle_id is not None:
            affected_vehicle_ids.add(snapshot_vehicle_id)
        snapshot_axle_number, snapshot_axle_side, snapshot_axle_dual_position = (
            tire.axle_number,
            tire.axle_side,
            tire.axle_dual_position,
        )
        tire.warehouse_id = warehouse_id

    elif movement_type in ("envio_reparacion", "envio_reencauche"):
        km_at_movement, snapshot_vehicle_id = await _read_current_position_km(db, tire)
        if snapshot_vehicle_id is not None:
            affected_vehicle_ids.add(snapshot_vehicle_id)
        snapshot_axle_number, snapshot_axle_side, snapshot_axle_dual_position = (
            tire.axle_number,
            tire.axle_side,
            tire.axle_dual_position,
        )
        tire.warehouse_id = None

    elif movement_type == "retorno_taller":
        if warehouse_id is None:
            raise InvalidTireMovement("'retorno_taller' requiere warehouse_id")
        snapshot_vehicle_id = None
        snapshot_axle_number = None
        snapshot_axle_side = None
        snapshot_axle_dual_position = None
        tire.warehouse_id = warehouse_id

    # Limpia la posición recién liberada (idempotente: en instalación ya se seteó arriba).
    if movement_type != "instalacion":
        tire.vehicle_id = None
        tire.axle_number = None
        tire.axle_side = None
        tire.axle_dual_position = None

    tire.status = TARGET_STATUS[movement_type]
    if thickness_mm is not None:
        tire.current_thickness_mm = thickness_mm

    movement = await tire_movement_crud.create(
        db,
        company_id=tire.company_id,
        tire_id=tire.id,
        movement_type=movement_type,
        vehicle_id=snapshot_vehicle_id,
        axle_number=snapshot_axle_number,
        axle_side=snapshot_axle_side,
        axle_dual_position=snapshot_axle_dual_position,
        warehouse_id=warehouse_id,
        provider_id=provider_id,
        km_at_movement=km_at_movement,
        thickness_mm=thickness_mm,
        notes=notes,
        recorded_by=recorded_by,
    )

    await db.commit()
    await db.refresh(tire)
    await db.refresh(movement)

    for vid in affected_vehicle_ids:
        await run_alert_checks(db, vehicle_ids=[vid])

    return movement


async def _read_current_position_km(db: AsyncSession, tire: Tire) -> tuple[int | None, uuid.UUID | None]:
    """Lee el km actual del vehículo donde está instalado el neumático (si lo hay). No modifica
    `tire` — el llamador limpia `vehicle_id`/posición por separado. Devuelve (km_at_movement,
    vehicle_id).
    """
    if tire.vehicle_id is None:
        return None, None
    vehicle = await vehicle_crud.get(db, tire.vehicle_id, tire.company_id)
    if vehicle is None:
        return None, tire.vehicle_id
    return vehicle.current_odometer_km, tire.vehicle_id
