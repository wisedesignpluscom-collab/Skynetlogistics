"""Endpoint público de ingesta GPS — el único de todo el sistema que no pasa por JWT.

Se autentica exclusivamente con el token propio del proveedor (`X-Webhook-Token`, ver
`crud/gps_provider.py::verify_webhook_token`), no con el auth de usuarios de la plataforma.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import gps_provider as gps_provider_crud
from app.crud import gps_provider_vehicle_map as gps_map_crud
from app.crud import vehicle as vehicle_crud
from app.crud import vehicle_position as vehicle_position_crud
from app.gps_adapters import get_adapter
from app.services.route_planning import check_deviation_and_recalculate
from app.services.vehicle_odometer import advance_odometer

router = APIRouter(prefix="/gps", tags=["gps"])


@router.post("/webhook/{provider_id}", status_code=status.HTTP_201_CREATED)
async def receive_gps_webhook(
    provider_id: uuid.UUID,
    payload: dict[str, Any],
    x_webhook_token: str | None = Header(default=None, alias="X-Webhook-Token"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    provider = await gps_provider_crud.get_by_id_any_company(db, provider_id)
    if provider is None or provider.ingestion_mode != "webhook" or not provider.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Proveedor GPS no encontrado")
    if x_webhook_token is None or not gps_provider_crud.verify_webhook_token(provider, x_webhook_token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token de webhook inválido")

    adapter = get_adapter(provider.adapter_type)
    try:
        normalized = adapter.normalize(payload)
    except (KeyError, ValueError, TypeError) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Payload inválido: {exc}") from None

    mapping = await gps_map_crud.get_by_external_device_id(db, provider.id, normalized.external_device_id)
    if mapping is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"external_device_id='{normalized.external_device_id}' no está mapeado a ningún vehículo",
        )

    await vehicle_position_crud.create(
        db,
        company_id=provider.company_id,
        vehicle_id=mapping.vehicle_id,
        provider_id=provider.id,
        position=normalized,
        raw_payload=payload,
    )

    if normalized.odometer_km is not None:
        vehicle = await vehicle_crud.get(db, mapping.vehicle_id, provider.company_id)
        if vehicle is not None:
            await advance_odometer(db, vehicle, normalized.odometer_km)

    # Recálculo automático por desvío (Fase 7): compara esta posición contra la ruta planeada del
    # viaje en curso y, si supera el umbral configurado, recalcula + genera alerta. Best-effort.
    await check_deviation_and_recalculate(
        db,
        vehicle_id=mapping.vehicle_id,
        company_id=provider.company_id,
        lat=normalized.lat,
        lng=normalized.lng,
        now=normalized.timestamp,
    )

    return {"status": "ok"}
