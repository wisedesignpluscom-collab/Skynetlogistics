import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.crud import gps_provider as gps_provider_crud
from app.crud import gps_provider_vehicle_map as gps_map_crud
from app.crud import vehicle as vehicle_crud
from app.models.user import User
from app.schemas.gps_provider import GPSProviderCreate, GPSProviderCreatedOut, GPSProviderOut, GPSProviderUpdate
from app.schemas.gps_provider_vehicle_map import GPSProviderVehicleMapCreate, GPSProviderVehicleMapOut

router = APIRouter(prefix="/gps-providers", tags=["gps"])


async def _get_provider_or_404(db: AsyncSession, provider_id: uuid.UUID, company_id: uuid.UUID):
    provider = await gps_provider_crud.get(db, provider_id, company_id)
    if provider is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Proveedor GPS no encontrado")
    return provider


@router.get("", response_model=list[GPSProviderOut])
async def list_gps_providers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("gps", "read")),
) -> list[GPSProviderOut]:
    return await gps_provider_crud.list_all_for_company(db, current_user.company_id)


@router.post("", response_model=GPSProviderCreatedOut, status_code=status.HTTP_201_CREATED)
async def create_gps_provider(
    payload: GPSProviderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("gps", "write")),
) -> GPSProviderCreatedOut:
    provider, raw_token = await gps_provider_crud.create(db, current_user.company_id, payload)
    return GPSProviderCreatedOut.model_validate(provider, from_attributes=True).model_copy(
        update={"webhook_token": raw_token}
    )


@router.get("/{provider_id}", response_model=GPSProviderOut)
async def get_gps_provider(
    provider_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("gps", "read")),
) -> GPSProviderOut:
    return await _get_provider_or_404(db, provider_id, current_user.company_id)


@router.patch("/{provider_id}", response_model=GPSProviderOut)
async def update_gps_provider(
    provider_id: uuid.UUID,
    payload: GPSProviderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("gps", "write")),
) -> GPSProviderOut:
    provider = await _get_provider_or_404(db, provider_id, current_user.company_id)
    return await gps_provider_crud.update(db, provider, payload)


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gps_provider(
    provider_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("gps", "delete")),
) -> None:
    provider = await _get_provider_or_404(db, provider_id, current_user.company_id)
    await gps_provider_crud.delete(db, provider)


@router.post("/{provider_id}/regenerate-token", response_model=GPSProviderCreatedOut)
async def regenerate_webhook_token(
    provider_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("gps", "write")),
) -> GPSProviderCreatedOut:
    provider = await _get_provider_or_404(db, provider_id, current_user.company_id)
    if provider.ingestion_mode != "webhook":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Este proveedor no usa autenticación por token webhook")
    raw_token = await gps_provider_crud.regenerate_webhook_token(db, provider)
    return GPSProviderCreatedOut.model_validate(provider, from_attributes=True).model_copy(
        update={"webhook_token": raw_token}
    )


@router.get("/{provider_id}/vehicle-map", response_model=list[GPSProviderVehicleMapOut])
async def list_vehicle_map(
    provider_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("gps", "read")),
) -> list[GPSProviderVehicleMapOut]:
    await _get_provider_or_404(db, provider_id, current_user.company_id)
    return await gps_map_crud.list_for_provider(db, provider_id)


@router.post(
    "/{provider_id}/vehicle-map", response_model=GPSProviderVehicleMapOut, status_code=status.HTTP_201_CREATED
)
async def create_vehicle_map(
    provider_id: uuid.UUID,
    payload: GPSProviderVehicleMapCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("gps", "write")),
) -> GPSProviderVehicleMapOut:
    await _get_provider_or_404(db, provider_id, current_user.company_id)
    if await vehicle_crud.get(db, payload.vehicle_id, current_user.company_id) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El vehículo no pertenece a esta empresa")
    if await gps_map_crud.get_by_external_device_id(db, provider_id, payload.external_device_id) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ese external_device_id ya está mapeado en este proveedor")
    return await gps_map_crud.create(db, provider_id, payload)


@router.delete("/{provider_id}/vehicle-map/{mapping_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle_map(
    provider_id: uuid.UUID,
    mapping_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("gps", "delete")),
) -> None:
    await _get_provider_or_404(db, provider_id, current_user.company_id)
    mapping = await gps_map_crud.get(db, mapping_id, provider_id)
    if mapping is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mapeo no encontrado")
    await gps_map_crud.delete(db, mapping)
