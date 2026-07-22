import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import vehicle_document_type as vehicle_document_type_crud
from app.models.user import User
from app.schemas.vehicle_document import (
    VehicleDocumentTypeCreate,
    VehicleDocumentTypeOut,
    VehicleDocumentTypeUpdate,
)

router = APIRouter(prefix="/vehicle-document-types", tags=["vehicles"])


@router.get("", response_model=list[VehicleDocumentTypeOut])
async def list_vehicle_document_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "read")),
) -> list[VehicleDocumentTypeOut]:
    return await vehicle_document_type_crud.list_all_for_company(db, current_user.company_id)


@router.post("", response_model=VehicleDocumentTypeOut, status_code=status.HTTP_201_CREATED)
async def create_vehicle_document_type(
    payload: VehicleDocumentTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "write")),
) -> VehicleDocumentTypeOut:
    return await vehicle_document_type_crud.create(db, current_user.company_id, payload)


@router.patch("/{type_id}", response_model=VehicleDocumentTypeOut)
async def update_vehicle_document_type(
    type_id: uuid.UUID,
    payload: VehicleDocumentTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "write")),
) -> VehicleDocumentTypeOut:
    doc_type = await vehicle_document_type_crud.get(db, type_id, current_user.company_id)
    if doc_type is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tipo de documento no encontrado")
    return await vehicle_document_type_crud.update(db, doc_type, payload)


@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle_document_type(
    type_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vehicles", "delete")),
) -> None:
    doc_type = await vehicle_document_type_crud.get(db, type_id, current_user.company_id)
    if doc_type is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tipo de documento no encontrado")
    await vehicle_document_type_crud.delete(db, doc_type)
