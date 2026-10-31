import hashlib, hmac
import pytest
from app.edge_adapter import signed_headers, publish

def test_hmac_payload_signature_is_reproducible():
    raw=b'{"event_type":"smoke_detected"}'
    secret="a"*40
    headers=signed_headers("sensor-1",secret,raw,timestamp=1700000000)
    expected=hmac.new(secret.encode(),b"1700000000\n"+raw,hashlib.sha256).hexdigest()
    assert headers["X-Device-Signature"]==expected
    assert headers["X-Sensor-ID"]=="sensor-1"

def test_weak_secret_rejected():
    with pytest.raises(ValueError):
        signed_headers("sensor-1","weak",b"{}",timestamp=1)

def test_plain_http_for_remote_is_rejected():
    with pytest.raises(ValueError):
        publish("http://untrusted.example","tower","sensor","x"*40,
                {"sensor_id":"sensor","external_id":"evt-1"})
