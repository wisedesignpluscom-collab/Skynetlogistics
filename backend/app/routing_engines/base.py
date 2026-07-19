"""Interfaz común para motores de ruteo (Fase 7).

Mismo patrón que `app/gps_adapters/` (Fase 3): agregar un motor nuevo (ej. OSRM self-hosted en
el futuro) es una clase que hereda de `RoutingEngine` + una entrada en `ENGINE_REGISTRY` (ver
`app/routing_engines/__init__.py`) — no requiere tocar el servicio de cálculo de ruta, los
endpoints ni el resto del sistema. El engine activo se elige con `settings.routing_engine`.

Las coordenadas se manejan en el orden (lat, lng) en toda la app; la geometría devuelta es una
lista de pares [lng, lat] (orden GeoJSON) lista para persistir en `route_plans.geometry` y para
que Leaflet la consuma tras invertir a [lat, lng] en el frontend.
"""

from abc import ABC, abstractmethod
from typing import ClassVar

from pydantic import BaseModel


class RouteResult(BaseModel):
    """Resultado normalizado de un cálculo de ruta punto a punto."""

    distance_km: float
    duration_min: int
    # GeoJSON LineString coords: [[lng, lat], ...]
    geometry: list[list[float]]


class RoutingEngine(ABC):
    engine_name: ClassVar[str]

    @abstractmethod
    async def route(
        self, *, origin_lat: float, origin_lng: float, destination_lat: float, destination_lng: float
    ) -> RouteResult:
        """Calcula la ruta óptima origen -> destino (sin paradas intermedias en 7A)."""
