"""Adapter para Traker GPS (modo webhook/push).

IMPORTANTE: no contamos con la documentación oficial de la API de Traker GPS al momento de
escribir esto. El mapeo de campos de `normalize()` es una suposición razonable basada en el
formato común de payloads de proveedores GPS (device_id, lat/lon, speed, odometer, ignition,
course, timestamp) — DEBE validarse y ajustarse contra la documentación real de Traker GPS
antes de usar en producción. El resto del sistema (webhook, endpoints de consulta, actualización
de odómetro) es agnóstico a este detalle: solo hay que corregir este archivo si el payload real
difiere.
"""

from datetime import datetime
from typing import Any

from app.gps_adapters.base import GPSProviderAdapter, NormalizedPosition


class TrakerGPSAdapter(GPSProviderAdapter):
    adapter_type = "traker_gps"

    def normalize(self, raw_payload: dict[str, Any]) -> NormalizedPosition:
        return NormalizedPosition(
            external_device_id=str(raw_payload["device_id"]),
            timestamp=datetime.fromisoformat(raw_payload["timestamp"]),
            lat=float(raw_payload["lat"]),
            lng=float(raw_payload["lon"]),
            speed_kmh=_optional_float(raw_payload.get("speed")),
            odometer_km=_optional_int(raw_payload.get("odometer")),
            ignition_status=raw_payload.get("ignition"),
            heading=_optional_int(raw_payload.get("course")),
        )


def _optional_float(value: Any) -> float | None:
    return None if value is None else float(value)


def _optional_int(value: Any) -> int | None:
    return None if value is None else int(value)
