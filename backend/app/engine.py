from datetime import datetime, timezone
from math import radians, sin, cos, sqrt, atan2
from .models import Event, Incident

THREAT_TYPES = {"possible_gunshot", "chainsaw", "wildfire", "animal_distress", "human_wildlife_conflict"}
CORRELATION_SECONDS = 15 * 60
CORRELATION_METERS = 1000

def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371000
    a, b = radians(lat1), radians(lat2)
    dl, dg = radians(lat2-lat1), radians(lon2-lon1)
    x = sin(dl/2)**2 + cos(a)*cos(b)*sin(dg/2)**2
    return 2*radius*atan2(sqrt(x), sqrt(max(0.0, 1-x)))

def priority(severity: int, event_type: str) -> str:
    if severity == 5 or (severity >= 4 and event_type in THREAT_TYPES):
        return "P1"
    if severity == 4 or severity == 3:
        return "P2"
    if severity == 2:
        return "P3"
    return "P4"

def correlate(event: Event, incidents: dict[str, Incident]) -> Incident | None:
    for candidate in sorted(incidents.values(), key=lambda item: item.updated_at, reverse=True):
        if candidate.status == "resolved" or candidate.event_type != event.event_type:
            continue
        if candidate.synthetic != event.synthetic:
            continue
        delta = abs((event.timestamp - candidate.updated_at).total_seconds())
        if delta <= CORRELATION_SECONDS and distance_m(event.latitude, event.longitude, candidate.latitude, candidate.longitude) <= CORRELATION_METERS:
            return candidate
    return None

def combine(event: Event, incident: Incident) -> Incident:
    # Independent sensor corroboration raises confidence modestly, not to certainty.
    independent = event.source_id not in incident.source_ids
    if independent:
        incident.source_ids.append(event.source_id)
    incident.event_ids.append(event.id)
    if event.modality.value not in incident.modalities:
        incident.modalities.append(event.modality.value)
    incident.confidence = round(min(0.99, max(incident.confidence, event.confidence) + (0.04 if independent else 0)), 3)
    incident.severity = max(incident.severity, event.severity)
    incident.priority = priority(incident.severity, event.event_type)
    incident.uncertainty_m = min(incident.uncertainty_m, event.uncertainty_m)
    incident.updated_at = datetime.now(timezone.utc)
    return incident
