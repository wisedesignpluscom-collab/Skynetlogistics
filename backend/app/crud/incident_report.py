import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident_report import IncidentReport, IncidentReportAttachment
from app.schemas.incident_report import IncidentReportCreate, IncidentReportUpdate


async def get(db: AsyncSession, incident_id: uuid.UUID, company_id: uuid.UUID) -> IncidentReport | None:
    result = await db.execute(
        select(IncidentReport).where(IncidentReport.id == incident_id, IncidentReport.company_id == company_id)
    )
    return result.scalar_one_or_none()


async def list_paginated(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    page: int,
    page_size: int,
    status: str | None = None,
    severity: str | None = None,
    type: str | None = None,
    driver_id: uuid.UUID | None = None,
) -> tuple[list[IncidentReport], int]:
    query = select(IncidentReport).where(IncidentReport.company_id == company_id)
    count_query = select(func.count()).select_from(IncidentReport).where(IncidentReport.company_id == company_id)

    if status:
        query = query.where(IncidentReport.status == status)
        count_query = count_query.where(IncidentReport.status == status)
    if severity:
        query = query.where(IncidentReport.severity == severity)
        count_query = count_query.where(IncidentReport.severity == severity)
    if type:
        query = query.where(IncidentReport.type == type)
        count_query = count_query.where(IncidentReport.type == type)
    if driver_id:
        query = query.where(IncidentReport.driver_id == driver_id)
        count_query = count_query.where(IncidentReport.driver_id == driver_id)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(IncidentReport.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def create(
    db: AsyncSession, company_id: uuid.UUID, driver_id: uuid.UUID, data: IncidentReportCreate
) -> IncidentReport:
    incident = IncidentReport(company_id=company_id, driver_id=driver_id, **data.model_dump())
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident


async def update_status(
    db: AsyncSession, incident: IncidentReport, data: IncidentReportUpdate, resolved_by: uuid.UUID | None
) -> IncidentReport:
    incident.status = data.status
    incident.resolution_notes = data.resolution_notes
    if data.status == "resuelto":
        incident.resolved_at = datetime.now(timezone.utc)
        incident.resolved_by = resolved_by
    else:
        incident.resolved_at = None
        incident.resolved_by = None
    await db.commit()
    await db.refresh(incident)
    return incident


async def add_attachment(
    db: AsyncSession, incident_report_id: uuid.UUID, file_url: str, uploaded_by: uuid.UUID | None
) -> IncidentReportAttachment:
    attachment = IncidentReportAttachment(
        incident_report_id=incident_report_id, file_url=file_url, uploaded_by=uploaded_by
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    return attachment


async def list_attachments(db: AsyncSession, incident_report_id: uuid.UUID) -> list[IncidentReportAttachment]:
    result = await db.execute(
        select(IncidentReportAttachment)
        .where(IncidentReportAttachment.incident_report_id == incident_report_id)
        .order_by(IncidentReportAttachment.created_at)
    )
    return list(result.scalars().all())
