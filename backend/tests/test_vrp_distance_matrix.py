import math

from app.services.vrp_distance_matrix import build_distance_matrix_m, estimate_route_km_and_min


def test_one_degree_of_latitude_at_equator_is_about_111_195_m() -> None:
    # Distancia de arco exacta: R * radians(1) con R=6_371_000 m (mismo radio que el resto del
    # proyecto) -> 111_194.9 m.
    matrix = build_distance_matrix_m([(0.0, 0.0), (1.0, 0.0)])
    assert abs(matrix[0][1] - 111_194.9) < 1.0


def test_matrix_is_symmetric_with_zero_diagonal() -> None:
    points = [(10.5, -66.9), (10.6, -71.6), (8.6, -71.1)]
    matrix = build_distance_matrix_m(points)
    for i in range(len(points)):
        assert matrix[i][i] == 0
        for j in range(len(points)):
            assert matrix[i][j] == matrix[j][i]


def test_single_point_matrix() -> None:
    matrix = build_distance_matrix_m([(0.0, 0.0)])
    assert matrix == [[0]]


def test_estimate_route_km_and_min_matches_hand_calculation() -> None:
    # Dos tramos de 1 grado de latitud cada uno (~111.19 km c/u) -> ~222.39 km total.
    # A 60 km/h: 222.39/60*60 = 222.39 min -> round = 222.
    km, minutes = estimate_route_km_and_min([(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)])
    assert abs(km - 222.39) < 0.1
    assert minutes == round(km / 60 * 60)


def test_estimate_route_of_single_point_is_zero() -> None:
    km, minutes = estimate_route_km_and_min([(10.0, -66.0)])
    assert km == 0.0
    assert minutes == 0
