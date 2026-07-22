import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import vehicle_document as vehicle_document_crud
from app.jobs.alerts import run_alert_checks
from app.models.user import User
from app.schemas.vehicle_document import VehicleDocumentOut, VehicleDocumentUpdate

router = APIRouter(prefix="/vehicle-documents", tags=["vehicles"])


@router.patch("/{document_id}", response_model=VehicleDocumentOut)
async def update_vehicle_document(
    document_id: uuid.UUID,
    payload: VehicleDocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "write")),
) -> VehicleDocumentOut:
    document = await vehicle_document_crud.get(db, document_id, current_user.company_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")
    updated = await vehicle_document_crud.update(db, document, payload)
    if payload.expiry_date is not None:
        await run_alert_checks(db, vehicle_ids=[updated.vehicle_id])
    return updated


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "delete")),
) -> None:
    document = await vehicle_document_crud.get(db, document_id, current_user.company_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")
    await vehicle_document_crud.delete(db, document)
