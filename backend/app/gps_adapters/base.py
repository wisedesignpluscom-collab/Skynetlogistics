"""Interfaz común para proveedores GPS (Fase 3).

Agregar un proveedor nuevo en el futuro es: una clase que hereda de `GPSProviderAdapter` +
una entrada en `ADAPTER_REGISTRY` (ver `app/gps_adapters/__init__.py`) — no requiere tocar
la ingesta (webhook/polling), los endpoints de consulta, ni el resto del sistema.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, ClassVar

from pydantic import BaseModel


class NormalizedPosition(BaseModel):
    """Forma común a la que todo adapter debe traducir el payload crudo del proveedor."""

    external_device_id: str
    timestamp: datetime
    lat: float
    lng: float
    speed_kmh: float | None = None
    odometer_km: int | None = None
    ignition_status: bool | None = None
    heading: int | None = None


class GPSProviderAdapter(ABC):
    adapter_type: ClassVar[str]

    @abstractmethod
    def normalize(self, raw_payload: dict[str, Any]) -> NormalizedPosition:
        """Traduce el payload crudo del proveedor (webhook o polling) a `NormalizedPosition`."""

    async def fetch_latest_positions(self, credentials: dict[str, Any]) -> list[dict[str, Any]]:
        """Solo para adapters de modo polling: devuelve una lista de payloads crudos
        (uno por posición) para pasar luego por `normalize()`. Los adapters de modo webhook
        no la implementan — el proveedor empuja los datos directamente."""
        raise NotImplementedError(f"{type(self).__name__} no soporta polling")
