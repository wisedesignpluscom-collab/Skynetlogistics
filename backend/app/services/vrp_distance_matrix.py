"""Matriz de distancias para el solver VRP (Fase 7B).

Función pura y determinista (sin red, sin DB) — mismo criterio que `route_geometry.py`: se puede
testear con coordenadas fijas contra valores calculados a mano. Usa haversine en vez de invocar el
motor de ruteo real (Mapbox) para no pagar N² llamadas de red durante el solve; la geometría/ruta
real de cada trip resultante se calcula aparte, una sola vez por vehículo, vía
`app/services/route_planning.py::compute_route_plan` (mismo motor que usa Fase 7A).
"""

import math

_EARTH_RADIUS_M = 6_371_000.0


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return _EARTH_RADIUS_M * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def estimate_route_km_and_min(
    points: list[tuple[float, float]], avg_speed_kmh: float = 60.0
) -> tuple[float, int]:
    """Estima distancia/duración totales de una secuencia de puntos vía haversine acumulado
    (mismo criterio de velocidad fija que `FakeRoutingEngine`) — solo para la propuesta del VRP
    antes de confirmar; la ruta real de cada vehículo confirmado se calcula con el motor activo
    vía `route_planning.compute_multi_stop_route_plan`."""
    total_km = 0.0
    for (lat1, lng1), (lat2, lng2) in zip(points, points[1:]):
        total_km += _haversine_m(lat1, lng1, lat2, lng2) / 1000.0
    duration_min = max(1, round(total_km / avg_speed_kmh * 60)) if total_km > 0 else 0
    return round(total_km, 2), duration_min


def build_distance_matrix_m(points: list[tuple[float, float]]) -> list[list[int]]:
    """Matriz NxN de distancias en metros (haversine, redondeada a entero) entre `points`
    (lista de tuplas (lat, lng)). OR-Tools RoutingModel requiere costos enteros."""
    n = len(points)
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        lat_i, lng_i = points[i]
        for j in range(i + 1, n):
            lat_j, lng_j = points[j]
            d = round(_haversine_m(lat_i, lng_i, lat_j, lng_j))
            matrix[i][j] = d
            matrix[j][i] = d
    return matrix
