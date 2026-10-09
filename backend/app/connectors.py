"""Optional interoperable intake using local event conversion. No false live connectivity."""
import json
from .models import EventIn
from .store import store

def ingest_mqtt_message(topic: str, payload: bytes, allowed_topics: set[str]) -> dict:
    if topic not in allowed_topics:
        raise ValueError("MQTT topic not authorized")
    if len(payload)>65536:
        raise ValueError("Message exceeds size limit")
    event=EventIn.model_validate(json.loads(payload))
    result=store.ingest(event)
    return {"event_id":result.id,"incident_id":result.incident_id,"synthetic":result.synthetic}

def export_incident_geojson(incidents) -> dict:
    return {"type":"FeatureCollection","features":[{
        "type":"Feature",
        "geometry":{"type":"Point","coordinates":[incident.longitude,incident.latitude]},
        "properties":{"id":incident.id,"priority":incident.priority,"status":incident.status,"synthetic":incident.synthetic}
    } for incident in incidents]}
