"""Catálogo de campos de SISTEMA "reglables" por entidad (Config-B).

Declara, para cada entidad, los campos base del formulario que las reglas pueden leer/afectar
(además de los campos custom de Config-A). Alimenta el endpoint `entity-schema` que el editor de
reglas usa para poblar los selectores de campo, y el contexto de evaluación.

Se mantiene a mano (no se refleja automáticamente del modelo) para exponer solo los campos que tiene
sentido reglar y con etiquetas legibles. Las opciones de los `select` se derivan de los enums del
modelo para no duplicar valores.
"""

from app.models.delivery_order import DELIVERY_ORDER_STATUSES
from app.models.driver import DRIVER_STATUSES, PAY_PERIODS
from app.models.maintenance_task import (
    MAINTENANCE_TASK_STATUSES,
    MAINTENANCE_TYPES,
    SCHEDULED_BY_OPTIONS,
)
from app.models.tire import TIRE_STATUSES
from app.models.vehicle import VEHICLE_STATUSES, VEHICLE_TYPES


def _opts(values: tuple[str, ...]) -> list[dict]:
    return [{"value": v, "label": v.replace("_", " ").capitalize()} for v in values]


# Cada entrada: {key, label, type, options?}. `type` usa el mismo vocabulario que los campos custom
# (texto/numero/fecha/select/checkbox) para que el editor y los evaluadores los traten igual.
SYSTEM_FIELDS: dict[str, list[dict]] = {
    "vehicle": [
        {"key": "type", "label": "Tipo", "type": "select", "options": _opts(VEHICLE_TYPES)},
        {"key": "status", "label": "Estado", "type": "select", "options": _opts(VEHICLE_STATUSES)},
        {"key": "brand", "label": "Marca", "type": "texto"},
        {"key": "model", "label": "Modelo", "type": "texto"},
        {"key": "year", "label": "Año", "type": "numero"},
        {"key": "cargo_capacity_kg", "label": "Capacidad (kg)", "type": "numero"},
        {"key": "cargo_capacity_m3", "label": "Capacidad (m³)", "type": "numero"},
    ],
    "driver": [
        {"key": "status", "label": "Estado", "type": "select", "options": _opts(DRIVER_STATUSES)},
        {"key": "license_expiry", "label": "Vencimiento licencia", "type": "fecha"},
        {"key": "base_salary", "label": "Salario base", "type": "numero"},
        {"key": "pay_period", "label": "Período de pago", "type": "select", "options": _opts(PAY_PERIODS)},
    ],
    "trip": [
        {"key": "cargo_type", "label": "Tipo de carga", "type": "texto"},
        {"key": "is_round_trip", "label": "Ida y vuelta", "type": "checkbox"},
        {"key": "distance_km", "label": "Distancia (km)", "type": "numero"},
    ],
    "delivery_order": [
        {"key": "priority", "label": "Prioridad", "type": "numero"},
        {"key": "status", "label": "Estado", "type": "select", "options": _opts(DELIVERY_ORDER_STATUSES)},
    ],
    "client": [
        {"key": "default_cargo_type", "label": "Tipo de carga por defecto", "type": "texto"},
        {"key": "is_active", "label": "Activo", "type": "checkbox"},
    ],
    "maintenance_task": [
        {"key": "type", "label": "Tipo", "type": "select", "options": _opts(MAINTENANCE_TYPES)},
        {"key": "scheduled_by", "label": "Programado por", "type": "select", "options": _opts(SCHEDULED_BY_OPTIONS)},
        {"key": "status", "label": "Estado", "type": "select", "options": _opts(MAINTENANCE_TASK_STATUSES)},
        {"key": "due_km", "label": "Km objetivo", "type": "numero"},
    ],
    "inventory_item": [
        {"key": "unit", "label": "Unidad", "type": "texto"},
        {"key": "min_stock", "label": "Stock mínimo", "type": "numero"},
        {"key": "unit_cost", "label": "Costo unitario", "type": "numero"},
    ],
    "tire": [
        {"key": "brand", "label": "Marca", "type": "texto"},
        {"key": "model", "label": "Modelo", "type": "texto"},
        {"key": "current_thickness_mm", "label": "Espesor (mm)", "type": "numero"},
        {"key": "status", "label": "Estado", "type": "select", "options": _opts(TIRE_STATUSES)},
    ],
    "delivery_goods": [
        {"key": "unit", "label": "Unidad", "type": "texto"},
        {"key": "min_stock", "label": "Stock mínimo", "type": "numero"},
        {"key": "unit_cost", "label": "Costo unitario", "type": "numero"},
        {"key": "weight_kg_per_unit", "label": "Peso por unidad (kg)", "type": "numero"},
        {"key": "volume_m3_per_unit", "label": "Volumen por unidad (m³)", "type": "numero"},
    ],
}


def system_fields_for(entity_type: str) -> list[dict]:
    return SYSTEM_FIELDS.get(entity_type, [])
