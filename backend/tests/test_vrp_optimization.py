from app.services.vrp_optimization import CapacityDimension, solve_vrp


def test_two_vehicles_get_their_nearby_stops() -> None:
    # Vehículo 0 en (-66,10), vehículo 1 en (-65,10); dos paradas pegadas a cada uno.
    vehicle_starts = [(10.0, -66.0), (10.0, -65.0)]
    stops = [
        (10.001, -65.999),  # cerca del vehículo 0
        (10.002, -65.998),  # cerca del vehículo 0
        (10.001, -65.001),  # cerca del vehículo 1
        (10.002, -65.002),  # cerca del vehículo 1
    ]
    assignment = solve_vrp(vehicle_starts=vehicle_starts, stops=stops)
    assert assignment is not None
    assert set(assignment[0]) == {0, 1}
    assert set(assignment[1]) == {2, 3}


def test_single_vehicle_gets_all_stops_in_some_order() -> None:
    vehicle_starts = [(10.0, -66.0)]
    stops = [(10.1, -66.1), (10.2, -66.2), (10.05, -66.05)]
    assignment = solve_vrp(vehicle_starts=vehicle_starts, stops=stops)
    assert assignment is not None
    assert len(assignment) == 1
    assert set(assignment[0]) == {0, 1, 2}


def test_no_stops_returns_empty_lists_per_vehicle() -> None:
    assignment = solve_vrp(vehicle_starts=[(10.0, -66.0), (10.0, -65.0)], stops=[])
    assert assignment == [[], []]


def test_no_vehicles_returns_empty_list() -> None:
    assignment = solve_vrp(vehicle_starts=[], stops=[(10.0, -66.0)])
    assert assignment == []


def test_capacity_splits_load_between_two_vehicles() -> None:
    # Dos paradas de 6 kg cada una y dos vehículos con capacidad 10 kg: no caben las dos en uno,
    # el solver debe repartir una a cada vehículo.
    vehicle_starts = [(10.0, -66.0), (10.1, -66.1)]
    stops = [(10.05, -66.05), (10.2, -66.2)]
    dim = CapacityDimension(name="kg", demands=[6, 6], capacities=[10, 10])
    assignment = solve_vrp(vehicle_starts=vehicle_starts, stops=stops, capacity_dims=[dim])
    assert assignment is not None
    assert sorted(len(a) for a in assignment) == [1, 1]


def test_capacity_infeasible_when_load_exceeds_fleet() -> None:
    # Un solo vehículo de 10 kg, dos paradas de 6 kg (=12 kg): no factible.
    dim = CapacityDimension(name="kg", demands=[6, 6], capacities=[10])
    assignment = solve_vrp(
        vehicle_starts=[(10.0, -66.0)], stops=[(10.05, -66.05), (10.2, -66.2)], capacity_dims=[dim]
    )
    assert assignment is None


def test_route_is_open_vehicle_does_not_pay_return_leg() -> None:
    # Una única parada muy lejos: el vehículo debe ir y quedarse ahí (ruta abierta), no hay
    # "vuelta" de regreso que optimizar — solo verificamos que la asignación sea trivial y única.
    vehicle_starts = [(0.0, 0.0)]
    stops = [(50.0, 50.0)]
    assignment = solve_vrp(vehicle_starts=vehicle_starts, stops=stops)
    assert assignment == [[0]]
