import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_driver, require_permission
from app.core.file_storage import save_incident_attachment
from app.core.websocket_manager import connection_manager
from app.crud import incident_report as incident_report_crud
from app.crud import trip as trip_crud
from app.crud import vehicle as vehicle_crud
from app.jobs.alerts import create_incident_alert
from app.models.driver import Driver
from app.models.user import User
from app.schemas.common import Page
from app.schemas.incident_report import (
    IncidentReportAttachmentOut,
    IncidentReportCreate,
    IncidentReportOut,
    IncidentReportUpdate,
)

router = APIRouter(prefix="/incident-reports", tags=["incident-reports"])


@router.get("", response_model=Page[IncidentReportOut])
async def list_incident_reports(
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = None,
    severity: str | None = None,
    type: str | None = None,
    driver_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("incidents", "read")),
) -> Page[IncidentReportOut]:
    items, total = await incident_report_crud.list_paginated(
        db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        status=status_filter,
        severity=severity,
        type=type,
        driver_id=driver_id,
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/mine", response_model=list[IncidentReportOut])
async def list_my_incident_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("incidents", "write")),
    current_driver: Driver = Depends(get_current_driver),
) -> list[IncidentReportOut]:
    items, _ = await incident_report_crud.list_paginated(
        db,
        company_id=current_user.company_id,
        page=1,
        page_size=200,
        driver_id=current_driver.id,
    )
    return items


@router.post("", response_model=IncidentReportOut, status_code=status.HTTP_201_CREATED)
async def create_incident_report(
    payload: IncidentReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("incidents", "write")),
    current_driver: Driver = Depends(get_current_driver),
) -> IncidentReportOut:
    if payload.vehicle_id is not None:
        if await vehicle_crud.get(db, payload.vehicle_id, current_user.company_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vehículo no encontrado")
    if payload.trip_id is not None:
        if await trip_crud.get(db, payload.trip_id, current_user.company_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Viaje no encontrado")

    incident = await incident_report_crud.create(db, current_user.company_id, current_driver.id, payload)

    if incident.severity in ("alta", "critica"):
        await create_incident_alert(db, incident)

    await connection_manager.broadcast_to_company(
        current_user.company_id,
        {"event": "incident_report_created", "incident_report_id": str(incident.id)},
    )
    return incident


@router.get("/{incident_id}", response_model=IncidentReportOut)
async def get_incident_report(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("incidents", "read")),
) -> IncidentReportOut:
    incident = await incident_report_crud.get(db, incident_id, current_user.company_id)
    if incident is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reporte no encontrado")
    return incident


@router.patch("/{incident_id}", response_model=IncidentReportOut)
async def update_incident_report(
    incident_id: uuid.UUID,
    payload: IncidentReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("incidents", "write")),
) -> IncidentReportOut:
    incident = await incident_report_crud.get(db, incident_id, current_user.company_id)
    if incident is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reporte no encontrado")
    updated = await incident_report_crud.update_status(db, incident, payload, current_user.id)

    await connection_manager.broadcast_to_driver(
        updated.driver_id,
        {"event": "incident_report_updated", "incident_report_id": str(updated.id), "status": updated.status},
    )
    return updated


@router.get("/{incident_id}/attachments", response_model=list[IncidentReportAttachmentOut])
async def list_incident_report_attachments(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("incidents", "read")),
) -> list[IncidentReportAttachmentOut]:
    incident = await incident_report_crud.get(db, incident_id, current_user.company_id)
    if incident is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reporte no encontrado")
    return await incident_report_crud.list_attachments(db, incident_id)


@router.post(
    "/{incident_id}/attachments",
    response_model=IncidentReportAttachmentOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_incident_report_attachment(
    incident_id: uuid.UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("incidents", "write")),
    current_driver: Driver = Depends(get_current_driver),
) -> IncidentReportAttachmentOut:
    incident = await incident_report_crud.get(db, incident_id, current_user.company_id)
    if incident is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reporte no encontrado")
    if incident.driver_id != current_driver.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Este reporte no te pertenece")

    try:
        file_url = await save_incident_attachment(current_user.company_id, incident_id, file)
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc

    return await incident_report_crud.add_attachment(db, incident_id, file_url, current_user.id)
