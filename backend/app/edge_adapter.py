"""Edge sensor adapter: sends preclassified metadata over HTTPS, not raw media.
This does not classify images/audio or claim to connect physical hardware.
"""
import hashlib, hmac, json, time
from urllib.request import Request, urlopen
from urllib.parse import urlsplit

def signed_headers(sensor_id: str, secret: str, body: bytes, timestamp: int | None = None):
    if len(secret) < 32:
        raise ValueError("Each device must have a strong independent secret")
    when = str(int(time.time()) if timestamp is None else timestamp)
    signature = hmac.new(secret.encode(), when.encode() + b"\n" + body, hashlib.sha256).hexdigest()
    return {"Content-Type": "application/json", "X-Sensor-ID": sensor_id,
            "X-Device-Timestamp": when, "X-Device-Signature": signature}

def publish(api_url: str, tower_id: str, sensor_id: str, secret: str, observation: dict):
    parsed = urlsplit(api_url)
    if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1"}:
        raise ValueError("HTTPS required outside local development")
    if observation.get("sensor_id") != sensor_id or not observation.get("external_id"):
        raise ValueError("Sensor ID and unique external ID required")
    raw = json.dumps(observation, separators=(",", ":"), sort_keys=True).encode()
    url = api_url.rstrip("/") + "/towers/" + tower_id + "/signed-observations"
    req = Request(url, data=raw, headers=signed_headers(sensor_id, secret, raw), method="POST")
    with urlopen(req, timeout=15) as response:
        return json.loads(response.read())
