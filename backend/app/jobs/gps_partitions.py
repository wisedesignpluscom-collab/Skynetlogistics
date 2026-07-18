"""Mantenimiento de particiones de `vehicle_positions` (Fase 3).

La migración inicial crea el mes actual + 2 siguientes. Esta función, corrida mensualmente
por el mismo `AsyncIOScheduler` del motor de alertas (Fase 1), asegura que siempre exista la
partición de 3 meses en el futuro — así la tabla nunca se queda sin partición donde insertar.
"""

from datetime import date, datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def _month_bounds(base: date, offset: int) -> tuple[date, date]:
    month_index = base.month - 1 + offset
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


async def ensure_future_partition(db: AsyncSession, *, months_ahead: int = 3, today: date | None = None) -> str:
    """Crea (si no existe) la partición del mes `months_ahead` a partir de hoy. Devuelve su nombre."""
    effective_today = today or datetime.now(timezone.utc).date()
    start, end = _month_bounds(effective_today, months_ahead)
    partition_name = f"vehicle_positions_y{start.year}m{start.month:02d}"
    await db.execute(
        text(
            f"CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF vehicle_positions "
            f"FOR VALUES FROM ('{start.isoformat()}') TO ('{end.isoformat()}')"
        )
    )
    await db.commit()
    return partition_name
