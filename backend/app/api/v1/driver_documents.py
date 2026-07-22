import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import driver_document as driver_document_crud
from app.jobs.alerts import run_alert_checks
from app.models.user import User
from app.schemas.driver_document import DriverDocumentOut, DriverDocumentUpdate

router = APIRouter(prefix="/driver-documents", tags=["drivers"])


@router.patch("/{document_id}", response_model=DriverDocumentOut)
async def update_driver_document(
    document_id: uuid.UUID,
    payload: DriverDocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "write")),
) -> DriverDocumentOut:
    document = await driver_document_crud.get(db, document_id, current_user.company_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")
    updated = await driver_document_crud.update(db, document, payload)
    if payload.expiry_date is not None:
        await run_alert_checks(db, driver_ids=[updated.driver_id])
    return updated


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "delete")),
) -> None:
    document = await driver_document_crud.get(db, document_id, current_user.company_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")
    await driver_document_crud.delete(db, document)
