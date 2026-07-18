from app.models.tire import Tire
from app.models.tire_movement import TireMovement
from app.services.tire_km import calculate_tire_km, close_periods, compute_performance


def _movement(movement_type: str, km_at_movement: int | None, tire_id=None) -> TireMovement:
    m = TireMovement(movement_type=movement_type, km_at_movement=km_at_movement, tire_id=tire_id)
    return m


def test_calculate_tire_km_open_period_uses_current_odometer() -> None:
    movements = [_movement("instalacion", 10_000)]
    km_current_period, km_lifetime_total = calculate_tire_km(movements, current_odometer_km=12_500)
    assert km_current_period == 2_500
    assert km_lifetime_total == 2_500


def test_calculate_tire_km_no_open_period_when_not_installed() -> None:
    movements = [_movement("instalacion", 10_000), _movement("desinstalacion", 13_000)]
    km_current_period, km_lifetime_total = calculate_tire_km(movements, current_odometer_km=None)
    assert km_current_period is None
    assert km_lifetime_total == 3_000


def test_calculate_tire_km_sums_multiple_periods() -> None:
    movements = [
        _movement("instalacion", 10_000),
        _movement("desinstalacion", 13_000),
        _movement("instalacion", 20_000),
        _movement("envio_reparacion", 24_500),
    ]
    km_current_period, km_lifetime_total = calculate_tire_km(movements, current_odometer_km=None)
    assert km_current_period is None
    assert km_lifetime_total == 3_000 + 4_500


def test_close_periods_ignores_movements_without_km() -> None:
    movements = [_movement("instalacion", None), _movement("desinstalacion", None)]
    periods, open_install_km = close_periods(movements)
    assert periods == []
    assert open_install_km is None


def test_compute_performance_groups_by_brand_model_and_end_reason() -> None:
    tire_a = Tire(unique_code="A", brand="Michelin", model="X Multi", current_thickness_mm=15)
    tire_b = Tire(unique_code="B", brand="Michelin", model="X Multi", current_thickness_mm=15)
    tire_a.id = "tire-a"
    tire_b.id = "tire-b"

    movements = [
        _movement("instalacion", 0, tire_id="tire-a"),
        _movement("envio_reencauche", 60_000, tire_id="tire-a"),
        _movement("instalacion", 0, tire_id="tire-b"),
        _movement("envio_reencauche", 80_000, tire_id="tire-b"),
    ]

    rows = compute_performance([tire_a, tire_b], movements)
    assert len(rows) == 1
    row = rows[0]
    assert row.brand == "Michelin"
    assert row.model == "X Multi"
    assert row.end_reason == "envio_reencauche"
    assert row.sample_count == 2
    assert row.avg_km == 70_000
