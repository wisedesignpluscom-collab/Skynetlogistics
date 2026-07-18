import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_superadmin
from app.crud import company as company_crud
from app.schemas.common import Page
from app.schemas.company import CompanyCreate, CompanyOut, CompanyUpdate

router = APIRouter(
    prefix="/companies", tags=["companies"], dependencies=[Depends(get_current_superadmin)]
)


@router.get("", response_model=Page[CompanyOut])
async def list_companies(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> Page[CompanyOut]:
    items, total = await company_crud.list_paginated(db, page=page, page_size=page_size, search=search)
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
async def create_company(payload: CompanyCreate, db: AsyncSession = Depends(get_db)) -> CompanyOut:
    if await company_crud.get_by_tax_id(db, payload.tax_id) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una empresa con ese tax_id")
    return await company_crud.create(db, payload)


@router.get("/{company_id}", response_model=CompanyOut)
async def get_company(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> CompanyOut:
    company = await company_crud.get(db, company_id)
    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Empresa no encontrada")
    return company


@router.patch("/{company_id}", response_model=CompanyOut)
async def update_company(
    company_id: uuid.UUID, payload: CompanyUpdate, db: AsyncSession = Depends(get_db)
) -> CompanyOut:
    company = await company_crud.get(db, company_id)
    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Empresa no encontrada")
    if payload.tax_id and payload.tax_id != company.tax_id:
        existing = await company_crud.get_by_tax_id(db, payload.tax_id)
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una empresa con ese tax_id")
    return await company_crud.update(db, company, payload)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    company = await company_crud.get(db, company_id)
    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Empresa no encontrada")
    await company_crud.deactivate(db, company)
