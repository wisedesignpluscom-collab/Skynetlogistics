from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import tire_settings as tire_settings_crud
from app.models.user import User
from app.schemas.tire_settings import TireSettingsOut, TireSettingsUpdate

router = APIRouter(prefix="/tire-settings", tags=["tires"])


@router.get("", response_model=TireSettingsOut)
async def get_tire_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "read")),
) -> TireSettingsOut:
    return await tire_settings_crud.get_or_create(db, current_user.company_id)


@router.patch("", response_model=TireSettingsOut)
async def update_tire_settings(
    payload: TireSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("tires", "write")),
) -> TireSettingsOut:
    settings = await tire_settings_crud.get_or_create(db, current_user.company_id)
    return await tire_settings_crud.update(db, settings, payload)
