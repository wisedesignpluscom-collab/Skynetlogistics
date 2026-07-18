"""Motor de fatiga del conductor (Fase 4).

Corre cada 30 minutos (ver `app/main.py`) y, para cada conductor activo, reconstruye sus
ventanas de manejo (`app/services/fatigue_calculations.py`), calcula el riesgo y hace upsert
en `driver_fatigue_logs`. Cuando el nivel es alto/crítico, genera una alerta reutilizando
`crud/alert.py::create_if_not_exists` (Fase 1) — mismo índice único parcial anti-duplicado,
sin lógica nueva de deduplicación.
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import driver_fatigue_log as fatigue_log_crud
from app.crud import fatigue_rule as fatigue_rule_crud
from app.crud.alert import create_if_not_exists
from app.models.driver import Driver
from app.models.fatigue_rule import FatigueRule
from app.models.vehicle import Vehicle
from app.services.fatigue_calculations import compute_driver_fatigue

logger = logging.getLogger("app.jobs.fatigue")

# Los 4 niveles de riesgo no calzan 1:1 con los 3 de severidad de alerts (Fase 1).
RISK_LEVEL_TO_SEVERITY = {"alto": "media", "critico": "alta"}


async def run_fatigue_checks(db: AsyncSession, *, now: datetime | None = None) -> dict[str, int]:
    effective_now = now or datetime.now(timezone.utc)

    drivers_result = await db.execute(select(Driver).where(Driver.status == "activo"))
    drivers = list(drivers_result.scalars().all())

    rules_cache: dict[uuid.UUID, FatigueRule] = {}
    processed = 0
    alerts_created = 0

    for driver in drivers:
        rule = rules_cache.get(driver.company_id)
        if rule is None:
            rule = await fatigue_rule_crud.get_or_create(db, driver.company_id)
            rules_cache[driver.company_id] = rule

        vehicle_result = await db.execute(select(Vehicle).where(Vehicle.assigned_driver_id == driver.id))
        vehicle = vehicle_result.scalar_one_or_none()

        breakdown = await compute_driver_fatigue(
            db,
            driver=driver,
            vehicle_id=vehicle.id if vehicle else None,
            rule=rule,
            now=effective_now,
        )
        if breakdown is None:
            continue

        await fatigue_log_crud.upsert(
            db,
            company_id=driver.company_id,
            driver_id=driver.id,
            log_date=effective_now.date(),
            **breakdown,
        )
        processed += 1

        severity = RISK_LEVEL_TO_SEVERITY.get(breakdown["risk_level"])
        if severity is not None:
            message = (
                f"Conductor {driver.name} en riesgo de fatiga {breakdown['risk_level']} "
                f"(score {breakdown['risk_score']})"
            )
            inserted = await create_if_not_exists(
                db,
                company_id=driver.company_id,
                type="driver_fatigue",
                entity_type="driver",
                entity_id=driver.id,
                message=message,
                severity=severity,
            )
            if inserted:
                alerts_created += 1

    return {"drivers_processed": processed, "alerts_created": alerts_created}
