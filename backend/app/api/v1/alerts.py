import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import alert as alert_crud
from app.models.user import User
from app.schemas.alert import AlertOut, UnreadCountOut
from app.schemas.common import Page

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=Page[AlertOut])
async def list_alerts(
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = None,
    severity: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("alerts", "read")),
) -> Page[AlertOut]:
    items, total = await alert_crud.list_paginated(
        db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        status=status_filter,
        severity=severity,
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/unread-count", response_model=UnreadCountOut)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("alerts", "read")),
) -> UnreadCountOut:
    count = await alert_crud.unread_count(db, current_user.company_id)
    return UnreadCountOut(count=count)


@router.patch("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_alerts_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("alerts", "write")),
) -> None:
    await alert_crud.mark_all_read(db, current_user.company_id)


@router.patch("/{alert_id}/read", response_model=AlertOut)
async def mark_alert_read(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("alerts", "write")),
) -> AlertOut:
    alert = await alert_crud.get(db, alert_id, current_user.company_id)
    if alert is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alerta no encontrada")
    return await alert_crud.mark_read(db, alert)
