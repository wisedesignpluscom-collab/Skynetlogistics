import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import company_holiday as company_holiday_crud
from app.models.user import User
from app.schemas.company_holiday import CompanyHolidayCreate, CompanyHolidayOut

router = APIRouter(prefix="/holidays", tags=["trip_settings"])


@router.get("", response_model=list[CompanyHolidayOut])
async def list_holidays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "read")),
) -> list[CompanyHolidayOut]:
    return await company_holiday_crud.list_all_for_company(db, current_user.company_id)


@router.post("", response_model=CompanyHolidayOut, status_code=status.HTTP_201_CREATED)
async def create_holiday(
    payload: CompanyHolidayCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "write")),
) -> CompanyHolidayOut:
    return await company_holiday_crud.create(db, current_user.company_id, payload)


@router.delete("/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holiday(
    holiday_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("trip_settings", "delete")),
) -> None:
    holiday = await company_holiday_crud.get(db, holiday_id, current_user.company_id)
    if holiday is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Feriado no encontrado")
    await company_holiday_crud.delete(db, holiday)
