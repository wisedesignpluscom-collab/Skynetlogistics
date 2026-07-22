import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDPKMixin

VRP_RUN_STATUSES = ("propuesto", "confirmado", "descartado")


class VrpRun(Base, UUIDPKMixin):
    """Corrida de optimización multi-vehículo (Fase 7B) — bitácora de auditoría, mismo criterio
    que `route_recalculations` (Fase 7A): registra la propuesta del solver antes de confirmar y,
    tras confirmar, los trips que efectivamente se crearon a partir de ella.
    """

    __tablename__ = "vrp_runs"
    __table_args__ = (CheckConstraint(f"status IN {VRP_RUN_STATUSES}", name="ck_vrp_runs_status"),)

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    # [{"lat": .., "lng": .., "label": ..}, ...] — paradas capturadas por el despachador.
    input_stops: Mapped[list] = mapped_column(JSONB, nullable=False)
    cargo_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # IDs (string) de los vehículos considerados como candidatos en esta corrida.
    vehicle_ids_considered: Mapped[list] = mapped_column(JSONB, nullable=False)
    # [{"vehicle_id", "driver_id", "stop_indices", "distance_km", "duration_min"}, ...] — salida
    # del solver antes de confirmar (distancia/duración estimadas con haversine, no con el motor
    # de ruteo real; la ruta real se calcula recién al confirmar, por vehículo).
    proposed_assignment: Mapped[list] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="propuesto")
    # IDs (string) de los trips creados al confirmar — vacío mientras status='propuesto'.
    result_trip_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
