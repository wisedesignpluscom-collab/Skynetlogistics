import uuid

from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class RoutePlan(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "route_plans"
    __table_args__ = (UniqueConstraint("trip_id", name="uq_route_plans_trip"),)

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    origin_lat: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    origin_lng: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    destination_lat: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    destination_lng: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    # GeoJSON LineString coords: [[lng, lat], ...] — necesaria para dibujar la ruta en el mapa
    # (Fase 3/Leaflet) y para el cálculo de desvío (app/services/route_geometry.py).
    geometry: Mapped[list] = mapped_column(JSONB, nullable=False)
    # Vacío [] en 7A; 7B (VRP multi-parada) lo llena con las paradas optimizadas.
    waypoints: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    calculated_distance_km: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    calculated_duration_min: Mapped[int] = mapped_column(Integer, nullable=False)
    engine_used: Mapped[str] = mapped_column(String(20), nullable=False)
