import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin


class RouteSettings(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "route_settings"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    # Metros de desvío de la polyline planeada que disparan un recálculo automático.
    deviation_threshold_m: Mapped[int] = mapped_column(Integer, nullable=False, default=150)
    # Minutos de espera tras un recálculo antes de permitir el siguiente para el mismo plan
    # (evita spamear route_recalculations mientras el conductor sigue fuera de ruta).
    recalc_cooldown_min: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
