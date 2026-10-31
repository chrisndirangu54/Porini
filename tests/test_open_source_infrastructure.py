"""Validate bundled optional service configuration without needing Docker."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_compose_is_not_exposed_by_default():
    text=(ROOT/"compose.opensource.yml").read_text()
    assert "PORINI_POSTGRES_PASSWORD:?" in text
    assert "PORINI_GRAFANA_PASSWORD:?" in text
    assert "PORINI_KEYCLOAK_PASSWORD:?" in text
    assert "127.0.0.1:8081:8080" in text
    assert "internal: true" in text
def test_mqtt_is_fail_closed_by_default():
    text=(ROOT/"infra/mosquitto.conf").read_text()
    assert "allow_anonymous false" in text
    assert "listener 1883 127.0.0.1" in text
