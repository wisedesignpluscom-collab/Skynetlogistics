"""Actualización de odómetro compartida entre el cierre de viaje (Fase 2) y la ingesta GPS (Fase 3).

Ambos flujos necesitan lo mismo: si llega una lectura de odómetro mayor a la actual del
vehículo, actualizarla y revalidar el mantenimiento programado por kilometraje. Esta función
concentra ese patrón en un solo lugar en vez de repetirlo en cada fase que lo necesite.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import vehicle as vehicle_crud
from app.jobs.alerts import run_alert_checks
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleUpdate


async def advance_odometer(db: AsyncSession, vehicle: Vehicle, new_odometer_km: int) -> bool:
    """Actualiza `vehicle.current_odometer_km` si `new_odometer_km` es mayor al actual y
    re-chequea el mantenimiento programado por km de ese vehículo (reutiliza Fase 1).

    Devuelve True si actualizó, False si `new_odometer_km` no superaba el valor actual
    (lectura ignorada, no es un error — puede pasar con datos GPS fuera de orden).
    """
    if new_odometer_km <= vehicle.current_odometer_km:
        return False
    await vehicle_crud.update(db, vehicle, VehicleUpdate(current_odometer_km=new_odometer_km))
    await run_alert_checks(db, vehicle_ids=[vehicle.id])
    return True
