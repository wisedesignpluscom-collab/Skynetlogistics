import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class VrpStopIn(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    label: str = Field(min_length=1, max_length=255)
    # En modo "desde pedidos" (9C) cada parada referencia el pedido que la origina, para poder
    # despacharlo al confirmar. Vacío en el modo de captura manual (7B).
    order_id: uuid.UUID | None = None


class VrpOptimizeRequest(BaseModel):
    # Modo 7B: paradas capturadas a mano. Modo 9C: order_ids de pedidos `pendiente`. Exactamente uno.
    stops: list[VrpStopIn] | None = Field(default=None, max_length=60)
    order_ids: list[uuid.UUID] | None = Field(default=None, max_length=60)
    cargo_type: str = Field(min_length=1, max_length=100)
    # None -> usa todos los vehículos disponibles (activos, con conductor, sin viaje en curso,
    # con posición GPS). Si viene, acota el pool a este subconjunto (aplicando los mismos filtros).
    vehicle_ids: list[uuid.UUID] | None = None
    # Solo aplica en modo pedidos: si True, el solver respeta la capacidad kg/m3 de cada vehículo.
    enforce_capacity: bool = True

    @model_validator(mode="after")
    def _one_mode(self) -> "VrpOptimizeRequest":
        has_stops = bool(self.stops)
        has_orders = bool(self.order_ids)
        if has_stops == has_orders:
            raise ValueError("Envía 'stops' (captura manual) o 'order_ids' (desde pedidos), no ambos ni ninguno")
        return self


class VrpProposedVehicleOut(BaseModel):
    vehicle_id: uuid.UUID
    driver_id: uuid.UUID
    stops: list[VrpStopIn]
    distance_km: float
    duration_min: int
    # Carga total asignada y capacidad del vehículo (9C) — None si no aplica (modo manual / sin límite).
    load_kg: float | None = None
    load_m3: float | None = None
    capacity_kg: float | None = None
    capacity_m3: float | None = None


class VrpRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    input_stops: list[VrpStopIn]
    cargo_type: str
    vehicle_ids_considered: list[uuid.UUID]
    proposed_assignment: list[VrpProposedVehicleOut]
    status: str
    result_trip_ids: list[uuid.UUID]
    created_by: uuid.UUID
    created_at: datetime
