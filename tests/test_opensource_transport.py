import pytest
from backend.app.opensource_transport import insert_observation, publish_observation
def test_database_missing_config_fails(monkeypatch):
    monkeypatch.delenv("POSTGIS_DSN",raising=False)
    with pytest.raises(RuntimeError):insert_observation({})
@pytest.mark.asyncio
async def test_messaging_missing_config_fails(monkeypatch):
    monkeypatch.delenv("PORINI_NATS_URL",raising=False)
    with pytest.raises(RuntimeError):await publish_observation({})
