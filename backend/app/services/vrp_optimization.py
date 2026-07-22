"""Solver VRP multi-vehículo (Fase 7B), vía Google OR-Tools.

Función pura (sin red/DB, recibe coordenadas y devuelve índices) para poder testearla con
matrices fijas — mismo criterio que `route_geometry.py` / `vrp_distance_matrix.py`. Resuelve un
mTSP sin restricciones de capacidad ni ventanas de tiempo (alcance acordado para 7B): asigna cada
parada a un vehículo y ordena las paradas de cada vehículo minimizando la distancia total.

Rutas abiertas: cada vehículo parte de su propia posición (`vehicle_starts[i]`, ej. su última
posición GPS) y NO necesita volver a ese punto. Se modela con el truco estándar de OR-Tools para
VRP abierto: cada vehículo tiene su propio nodo de partida también como nodo de "regreso", pero el
costo de cualquier arco hacia ese nodo de regreso se fija en 0 — así el solver nunca paga (ni por
lo tanto optimiza) el tramo de vuelta, y el resultado se recorta antes de llegar a él.
"""

from typing import NamedTuple

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from app.services.vrp_distance_matrix import build_distance_matrix_m

Point = tuple[float, float]


class CapacityDimension(NamedTuple):
    """Una dimensión de capacidad para el CVRP (Fase 9C): la demanda entera de cada parada y la
    capacidad entera de cada vehículo. Se usa una por magnitud restringida (peso, volumen).
    Los valores deben venir ya escalados a entero (OR-Tools no acepta floats); usar un tope grande
    para "capacidad ilimitada" de un vehículo sin límite declarado. `name` debe ser único."""

    name: str
    demands: list[int]  # alineado a `stops`
    capacities: list[int]  # alineado a `vehicle_starts`


def solve_vrp(
    *,
    vehicle_starts: list[Point],
    stops: list[Point],
    time_limit_seconds: int = 10,
    capacity_dims: list[CapacityDimension] | None = None,
) -> list[list[int]] | None:
    """Asigna y ordena `stops` (lat, lng) entre `vehicle_starts` (lat, lng), uno por vehículo.

    Devuelve una lista alineada a `vehicle_starts`: para cada vehículo, la lista de índices de
    `stops` en el orden óptimo a visitar (vacía si no le tocó ninguna). Devuelve None si el solver
    no encuentra una solución factible dentro del tiempo dado.

    `capacity_dims` (Fase 9C): si se pasan, el solver respeta la capacidad de cada vehículo por
    dimensión (CVRP) — un vehículo no recibe más carga de la que le cabe. Sin dimensiones, se
    comporta como el mTSP sin capacidad de Fase 7B (comportamiento idéntico por defecto).
    """
    num_vehicles = len(vehicle_starts)
    num_stops = len(stops)
    if num_vehicles == 0 or num_stops == 0:
        return [[] for _ in range(num_vehicles)]

    points = list(vehicle_starts) + list(stops)
    matrix = build_distance_matrix_m(points)

    starts = list(range(num_vehicles))
    ends = list(range(num_vehicles))  # nodo de partida de cada vehículo reutilizado como "regreso"

    manager = pywrapcp.RoutingIndexManager(len(points), num_vehicles, starts, ends)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        to_node = manager.IndexToNode(to_index)
        if to_node < num_vehicles:
            return 0  # arco de "regreso" al nodo de partida de un vehículo: gratis (ruta abierta)
        from_node = manager.IndexToNode(from_index)
        return matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    for dim in capacity_dims or []:
        def demand_callback(from_index: int, _demands=dim.demands) -> int:
            node = manager.IndexToNode(from_index)
            return 0 if node < num_vehicles else _demands[node - num_vehicles]

        demand_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_index,
            0,  # sin holgura
            list(dim.capacities),  # capacidad por vehículo
            True,  # el "acumulado" arranca en cero
            f"cap_{dim.name}",
        )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(time_limit_seconds)

    solution = routing.SolveWithParameters(search_parameters)
    if solution is None:
        return None

    assignment: list[list[int]] = []
    for vehicle_id in range(num_vehicles):
        index = solution.Value(routing.NextVar(routing.Start(vehicle_id)))
        stop_indices: list[int] = []
        while not routing.IsEnd(index):
            stop_indices.append(manager.IndexToNode(index) - num_vehicles)
            index = solution.Value(routing.NextVar(index))
        assignment.append(stop_indices)
    return assignment
