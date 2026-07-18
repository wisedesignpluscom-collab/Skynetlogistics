import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import expense_concept as expense_concept_crud
from app.models.user import User
from app.schemas.common import Page
from app.schemas.expense_concept import ExpenseConceptCreate, ExpenseConceptOut, ExpenseConceptUpdate

router = APIRouter(prefix="/expense-concepts", tags=["trip_settings"])


@router.get("", response_model=Page[ExpenseConceptOut])
async def list_expense_concepts(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "read")),
) -> Page[ExpenseConceptOut]:
    items, total = await expense_concept_crud.list_paginated(
        db, company_id=current_user.company_id, page=page, page_size=page_size
    )
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=ExpenseConceptOut, status_code=status.HTTP_201_CREATED)
async def create_expense_concept(
    payload: ExpenseConceptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "write")),
) -> ExpenseConceptOut:
    if await expense_concept_crud.get_by_name(db, current_user.company_id, payload.name) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un concepto con ese nombre")
    return await expense_concept_crud.create(db, current_user.company_id, payload)


@router.patch("/{concept_id}", response_model=ExpenseConceptOut)
async def update_expense_concept(
    concept_id: uuid.UUID,
    payload: ExpenseConceptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "write")),
) -> ExpenseConceptOut:
    concept = await expense_concept_crud.get(db, concept_id, current_user.company_id)
    if concept is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Concepto no encontrado")
    return await expense_concept_crud.update(db, concept, payload)


@router.delete("/{concept_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_concept(
    concept_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "delete")),
) -> None:
    concept = await expense_concept_crud.get(db, concept_id, current_user.company_id)
    if concept is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Concepto no encontrado")
    await expense_concept_crud.delete(db, concept)
