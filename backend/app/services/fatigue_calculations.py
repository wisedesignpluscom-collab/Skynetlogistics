"""Cálculo de fatiga del conductor (Fase 4).

Reconstruye ventanas de manejo a partir de `ignition_status` de `vehicle_positions` (Fase 3),
con fallback a `trips` (Fase 2) cuando no hay señal GPS del vehículo asignado. La fórmula de
`calculate_risk` es una función pura, reutilizada tanto por el job programado (que persiste)
como por cualquier vista de "preview" que se necesite más adelante — mismo patrón que
`app/services/trip_calculations.py`.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver import Driver
from app.models.fatigue_rule import FatigueRule
from app.models.trip import Trip
from app.models.vehicle_position import VehiclePosition

# Tolerancia a huecos de señal GPS: más de esto entre dos lecturas "encendido" corta la ventana.
MAX_GAP_MINUTES = 15
# Qué tan vieja puede ser la última lectura "encendido" para seguir considerando que el
# conductor está manejando *ahora mismo* (afecta solo a continuous_driving_min).
STALE_THRESHOLD_MINUTES = 30


@dataclass
class DrivingWindow:
    start: datetime
    end: datetime

    @property
    def minutes(self) -> float:
        return (self.end - self.start).total_seconds() / 60


async def _windows_from_positions(
    db: AsyncSession, vehicle_id: uuid.UUID, window_start: datetime, window_end: datetime
) -> list[DrivingWindow] | None:
    """Ventanas de manejo reconstruidas desde ignition_status. `None` si no hay ninguna
    posición GPS en el rango (para que el llamador use el fallback de trips)."""
    result = await db.execute(
        select(VehiclePosition.timestamp, VehiclePosition.ignition_status)
        .where(
            VehiclePosition.vehicle_id == vehicle_id,
            VehiclePosition.timestamp >= window_start,
            VehiclePosition.timestamp <= window_end,
        )
        .order_by(VehiclePosition.timestamp.asc())
    )
    rows = result.all()
    if not rows:
        return None

    windows: list[DrivingWindow] = []
    current_start: datetime | None = None
    last_true_ts: datetime | None = None

    for ts, ignition in rows:
        if ignition:
            if current_start is None:
                current_start = ts
            elif last_true_ts is not None and (ts - last_true_ts) > timedelta(minutes=MAX_GAP_MINUTES):
                windows.append(DrivingWindow(current_start, last_true_ts))
                current_start = ts
            last_true_ts = ts
        else:
            if current_start is not None and last_true_ts is not None:
                windows.append(DrivingWindow(current_start, ts))
            current_start = None
            last_true_ts = None

    if current_start is not None and last_true_ts is not None:
        windows.append(DrivingWindow(current_start, last_true_ts))

    return windows


async def _windows_from_trips(
    db: AsyncSession, driver_id: uuid.UUID, window_start: datetime, window_end: datetime, now: datetime
) -> list[DrivingWindow]:
    """Fallback cuando el vehículo no tiene ninguna señal GPS: usa [started_at, ended_at) de
    los viajes del conductor como aproximación gruesa (sobreestima manejo continuo porque no
    ve paradas dentro del viaje — es la dirección segura para un sistema de fatiga)."""
    result = await db.execute(
        select(Trip.started_at, Trip.ended_at).where(
            Trip.driver_id == driver_id,
            Trip.status.in_(("en_curso", "completado")),
            Trip.started_at.isnot(None),
            Trip.started_at <= window_end,
        )
    )
    windows: list[DrivingWindow] = []
    for started_at, ended_at in result.all():
        end = ended_at or now
        if end < window_start:
            continue
        start = max(started_at, window_start)
        end = min(end, window_end)
        if end > start:
            windows.append(DrivingWindow(start, end))
    return windows


def _clip_minutes(windows: list[DrivingWindow], lo: datetime, hi: datetime) -> float:
    total = 0.0
    for w in windows:
        start = max(w.start, lo)
        end = min(w.end, hi)
        if end > start:
            total += (end - start).total_seconds() / 60
    return total


def _generate_night_intervals(
    lo: datetime, hi: datetime, night_start_hour: int, night_end_hour: int
) -> list[tuple[datetime, datetime]]:
    """Un intervalo nocturno por día calendario tocado por [lo, hi], manejando el cruce de
    medianoche (ej. 22:00 → 05:00 del día siguiente). Los intervalos no se solapan entre sí."""
    if night_start_hour == night_end_hour:
        return []
    intervals: list[tuple[datetime, datetime]] = []
    day = (lo - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_day = hi.replace(hour=0, minute=0, second=0, microsecond=0)
    while day <= end_day:
        start_of_night = day + timedelta(hours=night_start_hour)
        if night_start_hour > night_end_hour:
            end_of_night = day + timedelta(days=1, hours=night_end_hour)
        else:
            end_of_night = day + timedelta(hours=night_end_hour)
        if end_of_night > lo and start_of_night < hi:
            intervals.append((max(start_of_night, lo), min(end_of_night, hi)))
        day += timedelta(days=1)
    return intervals


def _night_minutes(
    windows: list[DrivingWindow], lo: datetime, hi: datetime, night_start_hour: int, night_end_hour: int
) -> float:
    night_intervals = _generate_night_intervals(lo, hi, night_start_hour, night_end_hour)
    total = 0.0
    for w in windows:
        w_start, w_end = max(w.start, lo), min(w.end, hi)
        if w_end <= w_start:
            continue
        for n_start, n_end in night_intervals:
            overlap_start, overlap_end = max(w_start, n_start), min(w_end, n_end)
            if overlap_end > overlap_start:
                total += (overlap_end - overlap_start).total_seconds() / 60
    return total


def calculate_risk(
    *,
    continuous_driving_min: int,
    total_24h_min: int,
    total_7day_min: int,
    night_driving_min: int,
    rule: FatigueRule,
) -> tuple[float, str]:
    continuous_ratio = continuous_driving_min / (float(rule.max_continuous_hours) * 60)
    daily_ratio = total_24h_min / (float(rule.max_24h_hours) * 60)
    weekly_ratio = total_7day_min / (float(rule.max_7day_hours) * 60)

    base_score = max(continuous_ratio, daily_ratio, weekly_ratio) * 100
    night_ratio = (night_driving_min / total_24h_min) if total_24h_min > 0 else 0.0
    multiplier = 1 + (float(rule.night_driving_weight) - 1) * night_ratio
    risk_score = min(base_score * multiplier, 150)

    if risk_score >= 100:
        risk_level = "critico"
    elif risk_score >= 85:
        risk_level = "alto"
    elif risk_score >= 60:
        risk_level = "medio"
    else:
        risk_level = "bajo"

    return round(risk_score, 2), risk_level


async def compute_driver_fatigue(
    db: AsyncSession, *, driver: Driver, vehicle_id: uuid.UUID | None, rule: FatigueRule, now: datetime
) -> dict | None:
    """Devuelve el desglose calculado para este conductor, o `None` si no hay actividad de
    manejo en los últimos 7 días (en ese caso no se escribe fila en driver_fatigue_logs)."""
    window_7d_start = now - timedelta(days=7)
    window_24h_start = now - timedelta(hours=24)

    windows: list[DrivingWindow] | None = None
    if vehicle_id is not None:
        windows = await _windows_from_positions(db, vehicle_id, window_7d_start, now)
    if windows is None:
        windows = await _windows_from_trips(db, driver.id, window_7d_start, now, now)

    if not windows:
        return None

    total_7day_min = round(_clip_minutes(windows, window_7d_start, now))
    total_24h_min = round(_clip_minutes(windows, window_24h_start, now))
    night_driving_min = round(
        _night_minutes(windows, window_24h_start, now, rule.night_start_hour, rule.night_end_hour)
    )

    last_window = windows[-1]
    is_currently_driving = (now - last_window.end) <= timedelta(minutes=STALE_THRESHOLD_MINUTES)
    continuous_driving_min = round(last_window.minutes) if is_currently_driving else 0

    risk_score, risk_level = calculate_risk(
        continuous_driving_min=continuous_driving_min,
        total_24h_min=total_24h_min,
        total_7day_min=total_7day_min,
        night_driving_min=night_driving_min,
        rule=rule,
    )

    return {
        "continuous_driving_min": continuous_driving_min,
        "total_24h_min": total_24h_min,
        "total_7day_min": total_7day_min,
        "night_driving_min": night_driving_min,
        "risk_score": risk_score,
        "risk_level": risk_level,
    }
