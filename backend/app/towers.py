"""Porini Sentinel Towers prototype: review-first sensor observations and tower health.
In-memory registry, not suitable for emergency reliance or production deployment.
"""
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

class SensorKind(str, Enum):
    optical = "optical"
    infrared = "infrared"
    thermal = "thermal"
    acoustic = "acoustic"
    weather = "weather"
    smoke = "smoke"
    radar = "radar"

class TowerIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    height_m: float = Field(gt=0, le=200)
    power_type: str = Field(default="solar", max_length=60)
    connectivity_type: str = Field(default="lte", max_length=60)

class SensorIn(BaseModel):
    kind: SensorKind
    model: str = Field(min_length=2, max_length=120)
    bearing_deg: float | None = Field(default=None, ge=0, lt=360)
    range_m: float | None = Field(default=None, gt=0, le=50000)

class ObservationIn(BaseModel):
    sensor_id: str
    event_type: str = Field(min_length=3, max_length=100)
    confidence: float = Field(ge=0, le=1)
    severity: int = Field(ge=1, le=5)
    uncertainty_m: float = Field(default=250, ge=0, le=100000)
    external_id: str | None = Field(default=None, max_length=200)
    synthetic: bool = True
    notes: str | None = Field(default=None, max_length=1000)

class HealthIn(BaseModel):
    battery_percent: float | None = Field(default=None, ge=0, le=100)
    online: bool
    temperature_c: float | None = Field(default=None, ge=-80, le=120)

FIRE = {"smoke_detected", "thermal_fire_anomaly", "fire_detected", "possible_wildfire"}
ACOUSTIC = {"possible_gunshot", "chainsaw_detected", "vehicle_noise", "tree_fall_anomaly", "wildlife_distress"}
VISUAL = {"smoke_detected", "fire_detected", "possible_intrusion", "possible_vehicle", "vegetation_change"}
KNOWN = FIRE | ACOUSTIC | VISUAL

def bind_towers(store, allowed_role):
    from .models import EventIn
    router = APIRouter(prefix="/towers", tags=["Sentinel Towers"])
    towers = {}
    sensors = {}
    observations = []
    seen = set()

    @router.post("", status_code=201)
    def register_tower(payload: TowerIn, role=Depends(allowed_role("admin"))):
        tower_id = str(uuid4())
        tower = {"id": tower_id, **payload.model_dump(), "health": None}
        towers[tower_id] = tower
        store.log("tower.registered", role, {"tower_id": tower_id})
        return tower

    @router.get("")
    def list_towers(role=Depends(allowed_role("admin", "ranger"))):
        return list(towers.values())

    @router.post("/{tower_id}/sensors", status_code=201)
    def register_sensor(tower_id: str, payload: SensorIn, role=Depends(allowed_role("admin"))):
        if tower_id not in towers:
            raise HTTPException(404, "Tower not found")
        sensor_id = str(uuid4())
        item = {"id": sensor_id, "tower_id": tower_id, **payload.model_dump()}
        sensors[sensor_id] = item
        store.log("tower.sensor.registered", role, {"tower_id": tower_id, "sensor_id": sensor_id})
        return item

    @router.get("/{tower_id}/sensors")
    def list_sensors(tower_id: str, role=Depends(allowed_role("admin", "ranger"))):
        if tower_id not in towers:
            raise HTTPException(404, "Tower not found")
        return [s for s in sensors.values() if s["tower_id"] == tower_id]

    @router.post("/{tower_id}/health")
    def update_health(tower_id: str, payload: HealthIn, role=Depends(allowed_role("admin", "sensor"))):
        if tower_id not in towers:
            raise HTTPException(404, "Tower not found")
        status = {**payload.model_dump(), "observed_at": datetime.now(timezone.utc).isoformat()}
        towers[tower_id]["health"] = status
        store.log("tower.health", role, {"tower_id": tower_id, "online": payload.online})
        return status

    @router.post("/{tower_id}/observations", status_code=201)
    def ingest_observation(tower_id: str, payload: ObservationIn, role=Depends(allowed_role("admin", "sensor"))):
        tower = towers.get(tower_id)
        if tower is None:
            raise HTTPException(404, "Tower not found")
        sensor = sensors.get(payload.sensor_id)
        if sensor is None or sensor["tower_id"] != tower_id:
            raise HTTPException(422, "Sensor does not belong to tower")
        if payload.event_type not in KNOWN:
            raise HTTPException(422, "Unsupported event type")
        if sensor["kind"] == SensorKind.acoustic and payload.event_type not in ACOUSTIC:
            raise HTTPException(422, "Event type incompatible with acoustic sensor")
        if sensor["kind"] in (SensorKind.optical, SensorKind.infrared, SensorKind.thermal) and payload.event_type not in (FIRE | VISUAL):
            raise HTTPException(422, "Event type incompatible with visual sensor")
        dedup_key = (tower_id, payload.sensor_id, payload.external_id)
        if payload.external_id and dedup_key in seen:
            raise HTTPException(409, "Duplicate observation")
        event = store.ingest(EventIn(
            source_id="tower:" + tower_id + ":" + payload.sensor_id,
            modality="acoustic" if sensor["kind"] == SensorKind.acoustic else
                     "thermal" if sensor["kind"] in (SensorKind.thermal, SensorKind.infrared) else "iot" if sensor["kind"] in
                     (SensorKind.weather, SensorKind.smoke, SensorKind.radar) else "camera",
            event_type=payload.event_type,
            latitude=tower["latitude"], longitude=tower["longitude"],
            confidence=payload.confidence, severity=payload.severity,
            uncertainty_m=payload.uncertainty_m, external_id=payload.external_id,
            synthetic=payload.synthetic, notes=payload.notes))
        if payload.external_id:
            seen.add(dedup_key)
        item = {"id": str(uuid4()), "tower_id": tower_id, "sensor_id": payload.sensor_id,
                "event_id": event.id, "incident_id": event.incident_id,
                "event_type": payload.event_type, "confidence": payload.confidence,
                "synthetic": payload.synthetic, "review_required": True}
        observations.append(item)
        return item

    @router.get("/{tower_id}/observations")
    def list_observations(tower_id: str, role=Depends(allowed_role("admin", "ranger"))):
        if tower_id not in towers:
            raise HTTPException(404, "Tower not found")
        return [item for item in observations if item["tower_id"] == tower_id]

    return router
