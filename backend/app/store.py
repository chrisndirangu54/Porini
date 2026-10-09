from datetime import datetime, timezone, timedelta
from uuid import uuid4
from .models import Event, EventIn, Incident
from .engine import priority, correlate, combine

class MemoryStore:
    def __init__(self):
        self.events: dict[str, Event] = {}
        self.incidents: dict[str, Incident] = {}
        self.assignments: list[dict] = []
        self.missions: dict[str, dict] = {}
        self.audit: list[dict] = []
        self.dedup: dict[tuple[str, str], str] = {}

    def log(self, action: str, actor: str, details: dict):
        self.audit.append({"id": str(uuid4()), "time": datetime.now(timezone.utc).isoformat(), "action": action, "actor": actor, "details": details})

    def ingest(self, payload: EventIn) -> Event:
        key = (payload.source_id, payload.external_id) if payload.external_id else None
        if key and key in self.dedup:
            return self.events[self.dedup[key]]
        event = Event(**payload.model_dump())
        candidate = correlate(event, self.incidents)
        if candidate:
            incident = combine(event, candidate)
        else:
            incident = Incident(event_type=event.event_type, latitude=event.latitude, longitude=event.longitude,
                                priority=priority(event.severity, event.event_type), confidence=event.confidence,
                                severity=event.severity, uncertainty_m=event.uncertainty_m,
                                synthetic=event.synthetic, event_ids=[event.id], source_ids=[event.source_id], modalities=[event.modality.value],
                                created_at=event.timestamp, updated_at=event.timestamp)
            self.incidents[incident.id] = incident
        event.incident_id = incident.id
        self.events[event.id] = event
        if key:
            self.dedup[key] = event.id
        self.log("event.ingested", event.source_id, {"event_id": event.id, "incident_id": incident.id, "synthetic": event.synthetic})
        return event

    def seed_demo(self):
        if self.events:
            return
        samples = [
            ("acoustic-west-04", "acoustic", "possible_gunshot", -1.402, 36.812, .88, 5, 120, 9),
            ("camera-west-02", "camera", "possible_gunshot", -1.403, 36.813, .72, 4, 75, 8),
            ("acoustic-north-12", "acoustic", "chainsaw", -0.792, 37.109, .91, 4, 160, 21),
            ("thermal-river-07", "thermal", "human_wildlife_conflict", -1.220, 36.770, .84, 4, 65, 36),
            ("satellite-east-02", "satellite", "forest_loss", -0.951, 37.392, .93, 3, 800, 120),
            ("collar-elk-08", "collar", "movement_anomaly", -1.165, 36.983, .77, 2, 30, 50),
            ("iot-water-05", "iot", "water_level_low", -1.310, 36.920, .96, 2, 15, 90),
        ]
        for src, mode, kind, lat, lon, conf, sev, unc, mins in samples:
            self.ingest(EventIn(source_id=src, modality=mode, event_type=kind,
                 latitude=lat, longitude=lon, confidence=conf, severity=sev, uncertainty_m=unc,
                 timestamp=datetime.now(timezone.utc)-timedelta(minutes=mins), synthetic=True,
                 notes="Synthetic demonstration event — not field data"))
store = MemoryStore()
