import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.jobs.alerts import run_alert_checks
from app.jobs.gps_partitions import ensure_future_partition

logger = logging.getLogger("app.jobs")


async def _run_alert_checks_job() -> None:
    async with AsyncSessionLocal() as db:
        created = await run_alert_checks(db)
        logger.info("Alert checks run: %s", created)


async def _ensure_gps_partition_job() -> None:
    async with AsyncSessionLocal() as db:
        partition_name = await ensure_future_partition(db)
        logger.info("GPS partition ensured: %s", partition_name)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _run_alert_checks_job,
        CronTrigger(hour=6, minute=0),
        id="daily_alert_checks",
        replace_existing=True,
    )
    scheduler.add_job(
        _ensure_gps_partition_job,
        CronTrigger(day=1, hour=0, minute=30),
        id="monthly_gps_partition_maintenance",
        replace_existing=True,
    )
    scheduler.start()
    app.state.scheduler = scheduler
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title="Skynet Logistics — Fleet Management API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
