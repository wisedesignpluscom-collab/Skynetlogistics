from datetime import date

TRAFFIC_LIGHT_ACTIVE_STATUSES = ("pendiente", "en_proceso")


def compute_traffic_light(
    *,
    status: str,
    scheduled_by: str,
    due_date: date | None,
    due_km: int | None,
    vehicle_odometer_km: int | None,
    today: date,
    warning_days_threshold: int,
    warning_km_threshold: int,
) -> str | None:
    """Calcula el color del semáforo (verde/amarillo/rojo) de una tarea de mantenimiento.

    Devuelve None cuando el estado no admite semáforo (completada/cancelada) o
    faltan los datos necesarios para el cálculo (ej. odómetro del vehículo).
    """
    if status == "vencida":
        return "rojo"
    if status not in TRAFFIC_LIGHT_ACTIVE_STATUSES:
        return None

    if scheduled_by == "tiempo" and due_date is not None:
        days_left = (due_date - today).days
        if days_left <= 0:
            return "rojo"
        if days_left <= warning_days_threshold:
            return "amarillo"
        return "verde"

    if scheduled_by == "km" and due_km is not None and vehicle_odometer_km is not None:
        km_left = due_km - vehicle_odometer_km
        if km_left <= 0:
            return "rojo"
        if km_left <= warning_km_threshold:
            return "amarillo"
        return "verde"

    return None
