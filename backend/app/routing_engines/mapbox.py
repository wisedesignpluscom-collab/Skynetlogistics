"""Motor de ruteo sobre Mapbox Directions API (Fase 7).

Requiere `settings.mapbox_access_token`. Devuelve la geometría como GeoJSON LineString (coords
[lng, lat]) tal cual la entrega Mapbox, más distancia (km) y duración (min). Cualquier error de
red/HTTP se traduce a `RoutingEngineError` para que el llamador decida (ej. no bloquear la
creación del viaje si el cálculo de ruta falla).
"""

import httpx

from app.core.config import settings
from app.routing_engines.base import RouteResult, RoutingEngine

_BASE_URL = "https://api.mapbox.com/directions/v5/mapbox/driving"


class RoutingEngineError(RuntimeError):
    pass


class MapboxRoutingEngine(RoutingEngine):
    engine_name = "mapbox"

    async def route(
        self, *, origin_lat: float, origin_lng: float, destination_lat: float, destination_lng: float
    ) -> RouteResult:
        token = settings.mapbox_access_token
        if not token:
            raise RoutingEngineError("mapbox_access_token no configurado")

        coords = f"{origin_lng},{origin_lat};{destination_lng},{destination_lat}"
        url = f"{_BASE_URL}/{coords}"
        params = {
            "access_token": token,
            "geometries": "geojson",
            "overview": "full",
            "alternatives": "false",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            raise RoutingEngineError(f"Error consultando Mapbox Directions: {exc}") from exc

        routes = data.get("routes") or []
        if not routes:
            raise RoutingEngineError("Mapbox no devolvió ninguna ruta para esas coordenadas")

        route = routes[0]
        distance_km = route["distance"] / 1000.0
        duration_min = max(1, round(route["duration"] / 60.0))
        geometry = route["geometry"]["coordinates"]

        return RouteResult(
            distance_km=round(distance_km, 2), duration_min=duration_min, geometry=geometry
        )
