from datetime import datetime, timezone

import pytest

from app.gps_adapters.traker_gps import TrakerGPSAdapter


def test_normalize_maps_expected_fields() -> None:
    adapter = TrakerGPSAdapter()
    raw = {
        "device_id": "12345",
        "lat": 10.4806,
        "lon": -66.9036,
        "speed": 62.5,
        "odometer": 154320,
        "ignition": True,
        "course": 187,
        "timestamp": "2026-07-18T15:00:00+00:00",
    }
    position = adapter.normalize(raw)

    assert position.external_device_id == "12345"
    assert position.timestamp == datetime(2026, 7, 18, 15, 0, tzinfo=timezone.utc)
    assert position.lat == 10.4806
    assert position.lng == -66.9036
    assert position.speed_kmh == 62.5
    assert position.odometer_km == 154320
    assert position.ignition_status is True
    assert position.heading == 187


def test_normalize_handles_missing_optional_fields() -> None:
    adapter = TrakerGPSAdapter()
    raw = {
        "device_id": "999",
        "lat": 1.0,
        "lon": 2.0,
        "timestamp": "2026-01-01T00:00:00+00:00",
    }
    position = adapter.normalize(raw)
    assert position.speed_kmh is None
    assert position.odometer_km is None
    assert position.ignition_status is None
    assert position.heading is None


def test_normalize_missing_required_field_raises() -> None:
    adapter = TrakerGPSAdapter()
    with pytest.raises(KeyError):
        adapter.normalize({"lat": 1.0, "lon": 2.0, "timestamp": "2026-01-01T00:00:00+00:00"})
