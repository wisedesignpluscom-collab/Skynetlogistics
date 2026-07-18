"""Cálculo de km recorridos por neumático, compartido entre el detalle de neumático y la
analítica de rendimiento por marca/modelo — para que ambos usen exactamente la misma lógica
de emparejar cada 'instalacion' con el movimiento que la cierra, en vez de reimplementarla.
"""

import uuid
from dataclasses import dataclass

from app.models.tire import Tire
from app.models.tire_movement import TireMovement

CLOSING_MOVEMENT_TYPES = ("desinstalacion", "envio_reparacion", "envio_reencauche")
PERFORMANCE_END_REASONS = ("envio_reparacion", "envio_reencauche")


@dataclass
class TirePeriod:
    km: int
    end_reason: str


@dataclass
class TirePerformance:
    brand: str
    model: str
    end_reason: str
    sample_count: int
    avg_km: float


def close_periods(movements: list[TireMovement]) -> tuple[list[TirePeriod], int | None]:
    """Recorre los movimientos (orden cronológico ascendente) emparejando cada 'instalacion'
    con el siguiente movimiento que la cierra (desinstalación o envío a reparación/reencauche).

    Devuelve (periodos_cerrados, km_at_movement_de_instalacion_abierta_o_None) — el segundo
    valor es el punto de partida del período actual si el neumático sigue instalado al final
    de la lista de movimientos.
    """
    periods: list[TirePeriod] = []
    open_install_km: int | None = None

    for movement in movements:
        if movement.movement_type == "instalacion" and movement.km_at_movement is not None:
            open_install_km = movement.km_at_movement
        elif movement.movement_type in CLOSING_MOVEMENT_TYPES:
            if open_install_km is not None and movement.km_at_movement is not None:
                km = movement.km_at_movement - open_install_km
                if km > 0:
                    periods.append(TirePeriod(km=km, end_reason=movement.movement_type))
            open_install_km = None

    return periods, open_install_km


def calculate_tire_km(
    movements: list[TireMovement], current_odometer_km: int | None
) -> tuple[int | None, int]:
    """Devuelve (km_current_period, km_lifetime_total).

    `km_current_period` es None si el neumático no está instalado actualmente (no hay período
    abierto). `km_lifetime_total` suma todos los períodos cerrados más el período abierto (si
    lo hay y se conoce el odómetro actual del vehículo).
    """
    periods, open_install_km = close_periods(movements)
    lifetime_total = sum(period.km for period in periods)

    km_current_period: int | None = None
    if open_install_km is not None and current_odometer_km is not None:
        km_current_period = max(current_odometer_km - open_install_km, 0)
        lifetime_total += km_current_period

    return km_current_period, lifetime_total


def compute_performance(tires: list[Tire], movements: list[TireMovement]) -> list[TirePerformance]:
    """Rendimiento por marca/modelo: km promedio de los períodos de instalación que terminaron
    en envío a reparación o a reencauche (agrupados por separado). Reutiliza `close_periods`
    en vez de reimplementar el emparejamiento instalación→cierre.
    """
    movements_by_tire: dict[uuid.UUID, list[TireMovement]] = {}
    for movement in movements:
        movements_by_tire.setdefault(movement.tire_id, []).append(movement)

    tire_by_id = {tire.id: tire for tire in tires}

    buckets: dict[tuple[str, str, str], list[int]] = {}
    for tire_id, tire_movements in movements_by_tire.items():
        tire = tire_by_id.get(tire_id)
        if tire is None:
            continue
        periods, _ = close_periods(tire_movements)
        for period in periods:
            if period.end_reason not in PERFORMANCE_END_REASONS:
                continue
            key = (tire.brand, tire.model, period.end_reason)
            buckets.setdefault(key, []).append(period.km)

    rows = [
        TirePerformance(
            brand=brand,
            model=model,
            end_reason=end_reason,
            sample_count=len(kms),
            avg_km=sum(kms) / len(kms),
        )
        for (brand, model, end_reason), kms in buckets.items()
    ]
    rows.sort(key=lambda row: (row.brand, row.model, row.end_reason))
    return rows
