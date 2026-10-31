from app.towers import TowerIn, SensorIn, ObservationIn, HealthIn, KNOWN
from pydantic import ValidationError
import pytest

def test_tower_coordinates_and_height_validated():
    with pytest.raises(ValidationError):
        TowerIn(name="A", latitude=100, longitude=36, height_m=-2)
    assert TowerIn(name="Sentinel One", latitude=-1.2, longitude=36.8, height_m=24).height_m == 24

def test_sensor_bearing_and_type_validated():
    with pytest.raises(ValidationError):
        SensorIn(kind="acoustic", model="Microphone", bearing_deg=360)
    assert SensorIn(kind="infrared", model="IR camera").kind.value == "infrared"

def test_observations_keep_synthetic_flag_and_confidence_validation():
    assert ObservationIn(sensor_id="s", event_type="possible_gunshot", confidence=.6, severity=3).synthetic
    with pytest.raises(ValidationError):
        ObservationIn(sensor_id="s", event_type="chainsaw_detected", confidence=1.5, severity=3)
    assert "smoke_detected" in KNOWN

def test_health_validation():
    with pytest.raises(ValidationError):
        HealthIn(online=True, battery_percent=150)
