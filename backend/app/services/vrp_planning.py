"""Orquestación del VRP multi-vehículo (Fase 7B) + enlace CVRP con reparto (Fase 9C).

`propose_optimization` arma el pool de vehículos candidatos (activos, con conductor asignado, sin
viaje `en_curso` y con posición GPS conocida — su última posición es el punto de partida), corre
`vrp_optimization.solve_vrp` y guarda la propuesta en un `VrpRun` sin crear trips todavía.

Dos modos de entrada (mutuamente excluyentes):
- **manual (7B):** `stops` capturadas a mano — mTSP sin capacidad.
- **desde pedidos (9C):** `order_ids` de pedidos `pendiente`; cada pedido es una parada cuya demanda
  (peso/volumen, sumada de sus líneas × `delivery_goods`) alimenta el CVRP. El solver respeta la
  capacidad `cargo_capacity_kg/m3` de cada vehículo (si `enforce_capacity`).

`confirm_run` crea un trip por vehículo, calcula su ruta real y —en modo pedidos— despacha cada
pedido al trip vía `delivery_dispatch.assign_to_trip` (Fase 9B), que descuenta stock y marca el
pedido `asignado`. Reutiliza ese único punto de entrada en vez de tocar stock aquí.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import delivery_goods as delivery_goods_crud
from app.crud import delivery_order as delivery_order_crud
from app.crud import trip as trip_crud
from app.crud import vehicle_position as vehicle_position_crud
from app.crud import vrp_run as vrp_run_crud
from app.models.delivery_order import DeliveryOrder
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.models.vrp_run import VrpRun
from app.schemas.trip import TripCreate
from app.services import delivery_dispatch
from app.services.route_planning import compute_multi_stop_route_plan
from app.services.vrp_distance_matrix import estimate_route_km_and_min
from app.services.vrp_optimization import CapacityDimension, solve_vrp

MAX_STOPS_PER_RUN = 60
_SCALE = 1000  # kg/m3 -> enteros (gramos / litros) para OR-Tools
_UNLIMITED = 10**12  # tope para un vehículo sin capacidad declarada en una dimensión


def _scale(value: float) -> int:
    return int(round(value * _SCALE))


async def get_available_vehicles(db: AsyncSession, company_id: uuid.UUID) -> list[Vehicle]:
    """Vehículos candidatos para una corrida VRP: activos, con conductor asignado, sin viaje en
    curso y con al menos una posición GPS conocida (es su punto de partida para el solver)."""
    result = await db.execute(
        select(Vehicle).where(
            Vehicle.company_id == company_id,
            Vehicle.status == "activo",
            Vehicle.assigned_driver_id.isnot(None),
        )
    )
    candidates = list(result.scalars().all())
    if not candidates:
        return []

    busy_result = await db.execute(
        select(Trip.vehicle_id).where(Trip.company_id == company_id, Trip.status == "en_curso")
    )
    busy_ids = {row[0] for row in busy_result}

    positions = await vehicle_position_crud.get_latest_for_fleet(db, company_id)
    known_position_ids = {p.vehicle_id for p in positions}

    return [v for v in candidates if v.id not in busy_ids and v.id in known_position_ids]


async def _stops_and_demands_from_orders(
    db: AsyncSession, company_id: uuid.UUID, order_ids: list[uuid.UUID]
) -> tuple[list[dict], list[float], list[float]]:
    """Traduce pedidos `pendiente` a paradas + demanda de peso/volumen por parada."""
    goods = await delivery_goods_crud.list_paginated(
        db, company_id=company_id, page=1, page_size=1000
    )
    goods_by_id = {g.id: g for g in goods[0]}

    stops: list[dict] = []
    demands_kg: list[float] = []
    demands_m3: list[float] = []
    for order_id in order_ids:
        order = await delivery_order_crud.get(db, order_id, company_id)
        if order is None:
            raise ValueError(f"Pedido {order_id} no encontrado")
        if order.status != "pendiente":
            raise ValueError(f"El pedido en {order.address} no está pendiente (está '{order.status}')")

        weight = 0.0
        volume = 0.0
        for item in order.items:
            g = goods_by_id.get(item.goods_id)
            if g is not None:
                weight += float(item.quantity) * float(g.weight_kg_per_unit)
                volume += float(item.quantity) * float(g.volume_m3_per_unit)
        stops.append(
            {"lat": float(order.lat), "lng": float(order.lng), "label": order.address, "order_id": str(order.id)}
        )
        demands_kg.append(weight)
        demands_m3.append(volume)
    return stops, demands_kg, demands_m3


def _build_capacity_dims(
    vehicles: list[Vehicle], demands_kg: list[float], demands_m3: list[float]
) -> list[CapacityDimension]:
    """Arma las dimensiones de capacidad para el solver: incluye peso y/o volumen solo si al menos
    un vehículo del pool declara ese límite (a los demás se les da tope 'ilimitado')."""
    dims: list[CapacityDimension] = []
    if any(v.cargo_capacity_kg is not None for v in vehicles):
        caps = [_scale(float(v.cargo_capacity_kg)) if v.cargo_capacity_kg is not None else _UNLIMITED for v in vehicles]
        dims.append(CapacityDimension("kg", [_scale(d) for d in demands_kg], caps))
    if any(v.cargo_capacity_m3 is not None for v in vehicles):
        caps = [_scale(float(v.cargo_capacity_m3)) if v.cargo_capacity_m3 is not None else _UNLIMITED for v in vehicles]
        dims.append(CapacityDimension("m3", [_scale(d) for d in demands_m3], caps))
    return dims


async def propose_optimization(
    db: AsyncSession,
    *,
    company_id: uuid.UUID,
    created_by: uuid.UUID,
    stops: list[dict] | None,
    order_ids: list[uuid.UUID] | None,
    cargo_type: str,
    vehicle_ids: list[uuid.UUID] | None,
    enforce_capacity: bool = True,
) -> VrpRun:
    from_orders = bool(order_ids)
    demands_kg: list[float] = []
    demands_m3: list[float] = []
    if from_orders:
        stops, demands_kg, demands_m3 = await _stops_and_demands_from_orders(db, company_id, order_ids)
    stops = stops or []

    if not stops:
        raise ValueError("No hay paradas para optimizar")
    if len(stops) > MAX_STOPS_PER_RUN:
        raise ValueError(f"Máximo {MAX_STOPS_PER_RUN} paradas por corrida")

    available = await get_available_vehicles(db, company_id)
    if vehicle_ids is not None:
        wanted = set(vehicle_ids)
        available = [v for v in available if v.id in wanted]
    if not available:
        raise ValueError(
            "No hay vehículos disponibles para optimizar "
            "(activos, con conductor asignado, sin viaje en curso y con posición GPS)"
        )

    positions = await vehicle_position_crud.get_latest_for_fleet(db, company_id)
    position_by_vehicle = {p.vehicle_id: p for p in positions}

    vehicle_starts = [
        (float(position_by_vehicle[v.id].lat), float(position_by_vehicle[v.id].lng)) for v in available
    ]
    stop_points = [(s["lat"], s["lng"]) for s in stops]

    capacity_dims: list[CapacityDimension] = []
    if from_orders and enforce_capacity:
        capacity_dims = _build_capacity_dims(available, demands_kg, demands_m3)

    assignment = solve_vrp(
        vehicle_starts=vehicle_starts, stops=stop_points, capacity_dims=capacity_dims or None
    )
    if assignment is None:
        raise ValueError(
            "El solver no encontró una asignación factible — la carga puede exceder la capacidad "
            "total de los vehículos disponibles"
        )

    proposed: list[dict] = []
    for vehicle, stop_indices in zip(available, assignment):
        if not stop_indices:
            continue
        ordered_stops = [stops[i] for i in stop_indices]
        start = (float(position_by_vehicle[vehicle.id].lat), float(position_by_vehicle[vehicle.id].lng))
        distance_km, duration_min = estimate_route_km_and_min(
            [start] + [(s["lat"], s["lng"]) for s in ordered_stops]
        )
        entry = {
            "vehicle_id": str(vehicle.id),
            "driver_id": str(vehicle.assigned_driver_id),
            "stops": ordered_stops,
            "distance_km": distance_km,
            "duration_min": duration_min,
        }
        if from_orders:
            entry["load_kg"] = round(sum(demands_kg[i] for i in stop_indices), 3)
            entry["load_m3"] = round(sum(demands_m3[i] for i in stop_indices), 3)
            entry["capacity_kg"] = float(vehicle.cargo_capacity_kg) if vehicle.cargo_capacity_kg is not None else None
            entry["capacity_m3"] = float(vehicle.cargo_capacity_m3) if vehicle.cargo_capacity_m3 is not None else None
        proposed.append(entry)

    if not proposed:
        raise ValueError("El solver no asignó ninguna parada a los vehículos disponibles")

    return await vrp_run_crud.create(
        db,
        company_id=company_id,
        input_stops=stops,
        cargo_type=cargo_type,
        vehicle_ids_considered=[str(v.id) for v in available],
        proposed_assignment=proposed,
        created_by=created_by,
    )


async def confirm_run(db: AsyncSession, run: VrpRun) -> list[Trip]:
    if run.status != "propuesto":
        raise ValueError("Esta corrida ya fue confirmada o descartada")

    positions = await vehicle_position_crud.get_latest_for_fleet(db, run.company_id)
    position_by_vehicle = {str(p.vehicle_id): p for p in positions}

    trips: list[Trip] = []
    for item in run.proposed_assignment:
        origin_position = position_by_vehicle.get(item["vehicle_id"])
        if origin_position is None:
            raise ValueError(
                f"El vehículo {item['vehicle_id']} ya no tiene posición GPS conocida; "
                "descarta esta corrida y vuelve a optimizar"
            )

        stops = item["stops"]
        trip = await trip_crud.create(
            db,
            run.company_id,
            TripCreate(
                vehicle_id=uuid.UUID(item["vehicle_id"]),
                driver_id=uuid.UUID(item["driver_id"]),
                origin="Posición GPS del vehículo (VRP)",
                destination=stops[-1]["label"],
                cargo_type=run.cargo_type,
                is_round_trip=False,
            ),
            distance_km=None,
            freight_cost=None,
        )
        trips.append(trip)

        # Modo pedidos (9C): despacha cada pedido de la ruta a este trip (descuenta stock).
        await _dispatch_orders_to_trip(db, run.company_id, stops, trip, run.created_by)

        try:
            await compute_multi_stop_route_plan(
                db,
                company_id=run.company_id,
                trip_id=trip.id,
                origin_lat=float(origin_position.lat),
                origin_lng=float(origin_position.lng),
                stops=stops,
            )
        except Exception:  # noqa: BLE001 — no bloquear la creación del trip por un fallo de ruteo
            pass

    await vrp_run_crud.mark_confirmed(db, run, result_trip_ids=[str(t.id) for t in trips])
    return trips


async def _dispatch_orders_to_trip(
    db: AsyncSession, company_id: uuid.UUID, stops: list[dict], trip: Trip, created_by: uuid.UUID
) -> None:
    for stop in stops:
        order_id = stop.get("order_id")
        if not order_id:
            continue
        order: DeliveryOrder | None = await delivery_order_crud.get(db, uuid.UUID(order_id), company_id)
        if order is not None and order.status == "pendiente":
            await delivery_dispatch.assign_to_trip(db, order, trip, recorded_by=created_by)


__all__ = ["get_available_vehicles", "propose_optimization", "confirm_run", "MAX_STOPS_PER_RUN"]
