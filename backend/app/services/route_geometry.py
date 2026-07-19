"""Geometría de rutas: distancia de un punto GPS a la polyline planeada (Fase 7).

Función pura y determinista (sin red, sin DB) para poder testearla con coordenadas fijas contra
valores calculados a mano — mismo criterio que las fórmulas de nómina (Fase 2) y fatiga (Fase 4).

El cálculo del desvío usa una proyección equirectangular local (se escala la longitud por
`cos(lat_media)`) para convertir grados a metros y luego mide la distancia euclídea punto-a-segmento.
A la escala de cientos de metros el error de esta aproximación es <0.5%, suficiente para decidir si
un vehículo se salió de la vía planeada, y evita agregar una librería geoespacial pesada.

Convención de coordenadas de la geometría: lista de pares [lng, lat] (orden GeoJSON), tal como se
persiste en `route_plans.geometry`.
"""

import math

_METERS_PER_DEG_LAT = 111_320.0


def _project(lat: float, lng: float, ref_lat: float) -> tuple[float, float]:
    """Proyecta (lat, lng) en grados a (x, y) en metros con origen en (0, 0) y escala local."""
    x = math.radians(lng) * math.cos(math.radians(ref_lat)) * 6_371_000.0
    y = math.radians(lat) * 6_371_000.0
    return x, y


def _point_to_segment_m(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    """Distancia (metros) del punto P al segmento AB, todo ya en coordenadas proyectadas."""
    abx, aby = bx - ax, by - ay
    seg_len_sq = abx * abx + aby * aby
    if seg_len_sq == 0.0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * abx + (py - ay) * aby) / seg_len_sq
    t = max(0.0, min(1.0, t))
    proj_x, proj_y = ax + t * abx, ay + t * aby
    return math.hypot(px - proj_x, py - proj_y)


def distance_to_polyline_m(lat: float, lng: float, geometry: list[list[float]]) -> float:
    """Distancia mínima (metros) del punto (lat, lng) a la polyline `geometry` ([[lng, lat], ...]).

    Devuelve `inf` si la geometría está vacía; con un solo punto, la distancia a ese punto.
    """
    if not geometry:
        return math.inf

    ref_lat = lat
    px, py = _project(lat, lng, ref_lat)

    if len(geometry) == 1:
        ax, ay = _project(geometry[0][1], geometry[0][0], ref_lat)
        return math.hypot(px - ax, py - ay)

    best = math.inf
    for (lng_a, lat_a), (lng_b, lat_b) in zip(geometry, geometry[1:]):
        ax, ay = _project(lat_a, lng_a, ref_lat)
        bx, by = _project(lat_b, lng_b, ref_lat)
        d = _point_to_segment_m(px, py, ax, ay, bx, by)
        if d < best:
            best = d
    return best


def is_off_route(lat: float, lng: float, geometry: list[list[float]], threshold_m: float) -> bool:
    """True si el punto está a más de `threshold_m` metros de la polyline planeada."""
    return distance_to_polyline_m(lat, lng, geometry) > threshold_m
