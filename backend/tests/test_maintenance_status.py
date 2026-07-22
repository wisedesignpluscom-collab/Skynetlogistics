from datetime import date

from app.services.maintenance_status import compute_traffic_light

_TODAY = date(2026, 7, 19)


def test_date_scheduled_task_far_from_due_is_green() -> None:
    result = compute_traffic_light(
        status="pendiente",
        scheduled_by="tiempo",
        due_date=date(2026, 8, 30),
        due_km=None,
        vehicle_odometer_km=None,
        today=_TODAY,
        warning_days_threshold=7,
        warning_km_threshold=500,
    )
    assert result == "verde"


def test_date_scheduled_task_within_warning_threshold_is_yellow() -> None:
    result = compute_traffic_light(
        status="pendiente",
        scheduled_by="tiempo",
        due_date=date(2026, 7, 24),
        due_km=None,
        vehicle_odometer_km=None,
        today=_TODAY,
        warning_days_threshold=7,
        warning_km_threshold=500,
    )
    assert result == "amarillo"


def test_date_scheduled_task_overdue_is_red() -> None:
    result = compute_traffic_light(
        status="pendiente",
        scheduled_by="tiempo",
        due_date=date(2026, 7, 10),
        due_km=None,
        vehicle_odometer_km=None,
        today=_TODAY,
        warning_days_threshold=7,
        warning_km_threshold=500,
    )
    assert result == "rojo"


def test_km_scheduled_task_uses_odometer_thresholds() -> None:
    green = compute_traffic_light(
        status="en_proceso",
        scheduled_by="km",
        due_date=None,
        due_km=100_000,
        vehicle_odometer_km=90_000,
        today=_TODAY,
        warning_days_threshold=7,
        warning_km_threshold=500,
    )
    yellow = compute_traffic_light(
        status="en_proceso",
        scheduled_by="km",
        due_date=None,
        due_km=100_000,
        vehicle_odometer_km=99_800,
        today=_TODAY,
        warning_days_threshold=7,
        warning_km_threshold=500,
    )
    red = compute_traffic_light(
        status="en_proceso",
        scheduled_by="km",
        due_date=None,
        due_km=100_000,
        vehicle_odometer_km=100_500,
        today=_TODAY,
        warning_days_threshold=7,
        warning_km_threshold=500,
    )
    assert (green, yellow, red) == ("verde", "amarillo", "rojo")


def test_status_vencida_is_always_red_regardless_of_dates() -> None:
    result = compute_traffic_light(
        status="vencida",
        scheduled_by="tiempo",
        due_date=date(2027, 1, 1),
        due_km=None,
        vehicle_odometer_km=None,
        today=_TODAY,
        warning_days_threshold=7,
        warning_km_threshold=500,
    )
    assert result == "rojo"


def test_completed_or_cancelled_tasks_have_no_traffic_light() -> None:
    for status in ("completada", "cancelada"):
        result = compute_traffic_light(
            status=status,
            scheduled_by="tiempo",
            due_date=date(2020, 1, 1),
            due_km=None,
            vehicle_odometer_km=None,
            today=_TODAY,
            warning_days_threshold=7,
            warning_km_threshold=500,
        )
        assert result is None


def test_km_scheduled_task_without_vehicle_odometer_returns_none() -> None:
    result = compute_traffic_light(
        status="pendiente",
        scheduled_by="km",
        due_date=None,
        due_km=100_000,
        vehicle_odometer_km=None,
        today=_TODAY,
        warning_days_threshold=7,
        warning_km_threshold=500,
    )
    assert result is None
