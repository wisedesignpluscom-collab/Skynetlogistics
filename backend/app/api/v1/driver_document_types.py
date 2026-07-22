import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import driver_document_type as driver_document_type_crud
from app.models.user import User
from app.schemas.driver_document import (
    DriverDocumentTypeCreate,
    DriverDocumentTypeOut,
    DriverDocumentTypeUpdate,
)

router = APIRouter(prefix="/driver-document-types", tags=["drivers"])


@router.get("", response_model=list[DriverDocumentTypeOut])
async def list_driver_document_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "read")),
) -> list[DriverDocumentTypeOut]:
    return await driver_document_type_crud.list_all_for_company(db, current_user.company_id)


@router.post("", response_model=DriverDocumentTypeOut, status_code=status.HTTP_201_CREATED)
async def create_driver_document_type(
    payload: DriverDocumentTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "write")),
) -> DriverDocumentTypeOut:
    return await driver_document_type_crud.create(db, current_user.company_id, payload)


@router.patch("/{type_id}", response_model=DriverDocumentTypeOut)
async def update_driver_document_type(
    type_id: uuid.UUID,
    payload: DriverDocumentTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "write")),
) -> DriverDocumentTypeOut:
    doc_type = await driver_document_type_crud.get(db, type_id, current_user.company_id)
    if doc_type is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tipo de documento no encontrado")
    return await driver_document_type_crud.update(db, doc_type, payload)


@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver_document_type(
    type_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("drivers", "delete")),
) -> None:
    doc_type = await driver_document_type_crud.get(db, type_id, current_user.company_id)
    if doc_type is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tipo de documento no encontrado")
    await driver_document_type_crud.delete(db, doc_type)
