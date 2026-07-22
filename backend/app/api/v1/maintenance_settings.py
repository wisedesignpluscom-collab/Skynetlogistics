from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import maintenance_settings as maintenance_settings_crud
from app.models.user import User
from app.schemas.maintenance_settings import MaintenanceSettingsOut, MaintenanceSettingsUpdate

router = APIRouter(prefix="/maintenance-settings", tags=["maintenance"])


@router.get("", response_model=MaintenanceSettingsOut)
async def get_maintenance_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("maintenance", "read")),
) -> MaintenanceSettingsOut:
    return await maintenance_settings_crud.get_or_create(db, current_user.company_id)


@router.patch("", response_model=MaintenanceSettingsOut)
async def update_maintenance_settings(
    payload: MaintenanceSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("maintenance", "write")),
) -> MaintenanceSettingsOut:
    settings = await maintenance_settings_crud.get_or_create(db, current_user.company_id)
    return await maintenance_settings_crud.update(db, settings, payload)
