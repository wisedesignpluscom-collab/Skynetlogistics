import math

from app.services.route_geometry import distance_to_polyline_m, is_off_route

# Polyline recta sobre el ecuador de (lat=0,lng=0) a (lat=0,lng=1) — geometría en orden [lng, lat].
_EQUATOR_LINE = [[0.0, 0.0], [1.0, 0.0]]


def test_point_on_the_line_is_zero() -> None:
    assert distance_to_polyline_m(0.0, 0.5, _EQUATOR_LINE) < 0.01


def test_point_north_of_line_matches_expected_meters() -> None:
    # 0.001 grados de latitud ≈ 111.32 m; la proyección local da ~111.2 m (<0.5% error).
    d = distance_to_polyline_m(0.001, 0.5, _EQUATOR_LINE)
    assert abs(d - 111.32) < 1.0


def test_point_beyond_endpoint_uses_endpoint_distance() -> None:
    # lng=1.5 está 0.5 grados más allá del extremo B=(lng=1,lat=0): ~55.6 km.
    d = distance_to_polyline_m(0.0, 1.5, _EQUATOR_LINE)
    assert abs(d - 55_660) < 500


def test_empty_geometry_is_infinite() -> None:
    assert distance_to_polyline_m(0.0, 0.0, []) == math.inf


def test_single_point_geometry() -> None:
    d = distance_to_polyline_m(0.001, 0.0, [[0.0, 0.0]])
    assert abs(d - 111.32) < 1.0


def test_is_off_route_threshold() -> None:
    # ~111 m de desvío
    assert is_off_route(0.001, 0.5, _EQUATOR_LINE, threshold_m=50) is True
    assert is_off_route(0.001, 0.5, _EQUATOR_LINE, threshold_m=150) is False


def test_nearest_segment_of_multi_segment_polyline() -> None:
    # L-shape: (0,0) -> (0,1) horizontal, luego (0,1) -> (1,1) vertical [lng,lat]
    geom = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]]
    # Punto cerca del segmento vertical, lejos del horizontal
    d = distance_to_polyline_m(0.5, 1.001, geom)
    assert abs(d - 111.32) < 1.5
