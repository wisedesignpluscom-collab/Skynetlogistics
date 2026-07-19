"""Motor de ruteo determinista en-memoria para desarrollo y tests (sin red).

Genera una polyline recta interpolada entre origen y destino y estima distancia/duración con la
fórmula de haversine + una velocidad media fija. No pretende ser realista — solo determinista y
reproducible, para poder testear el flujo completo (auto-trigger, desvío, recálculo) sin depender
de Mapbox ni de conectividad, igual que la suite hermética del resto del proyecto.
"""

import math

from app.routing_engines.base import RouteResult, RoutingEngine

_INTERPOLATION_POINTS = 20
_AVG_SPEED_KMH = 60.0


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class FakeRoutingEngine(RoutingEngine):
    engine_name = "fake"

    async def route(
        self, *, origin_lat: float, origin_lng: float, destination_lat: float, destination_lng: float
    ) -> RouteResult:
        distance_km = _haversine_km(origin_lat, origin_lng, destination_lat, destination_lng)
        duration_min = max(1, round(distance_km / _AVG_SPEED_KMH * 60))

        geometry: list[list[float]] = []
        for i in range(_INTERPOLATION_POINTS + 1):
            t = i / _INTERPOLATION_POINTS
            lat = origin_lat + (destination_lat - origin_lat) * t
            lng = origin_lng + (destination_lng - origin_lng) * t
            geometry.append([round(lng, 6), round(lat, 6)])

        return RouteResult(
            distance_km=round(distance_km, 2), duration_min=duration_min, geometry=geometry
        )
