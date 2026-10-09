"""Conservation modules: strictly observational, human-reviewed workflows."""
import json
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

router = APIRouter(prefix="/v1")
_lock = threading.RLock()
DB = os.environ.get("PORINI_DB_PATH", "/tmp/porini_extensions.sqlite3")

def connection():
    db = sqlite3.connect(DB, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""CREATE TABLE IF NOT EXISTS records (
       id TEXT PRIMARY KEY, tenant TEXT NOT NULL, kind TEXT NOT NULL,
       created TEXT NOT NULL, payload TEXT NOT NULL)""")
    db.execute("CREATE INDEX IF NOT EXISTS by_tenant_kind ON records(tenant,kind)")
    return db

class ConservationRecord(BaseModel):
    kind: Literal["sensor","camera_trap","satellite_scene","species_sighting","habitat_change",
                  "waterhole","wildfire","collar","animal_health","community_report",
                  "ranger_patrol","device_health","acoustic_detection","mission_plan",
                  "research_dataset","wildlife_corridor","restoration","veterinary_case",
                  "eco_indicator","conservation_zone","model_registry","notification",
                  "integration_config","data_quality","training_annotation"]
    tenant: str = Field(min_length=3, max_length=100)
    source: str = Field(min_length=2, max_length=120)
    observed_at: datetime
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    confidence: float | None = Field(None, ge=0, le=1)
    synthetic: bool = False
    privacy: Literal["internal","sensitive","public_aggregate"] = "internal"
    status: Literal["unverified","verified","rejected"] = "unverified"
    metadata: dict = Field(default_factory=dict)

class Review(BaseModel):
    status: Literal["verified","rejected"]
    reviewer: str = Field(min_length=3, max_length=120)
    rationale: str = Field(min_length=5, max_length=1000)

def _authorize(tenant: str, role: str, scope: str):
    if role not in ("admin","ranger","sensor"):
        raise HTTPException(403,"Invalid role")
    if scope == "review" and role != "admin":
        raise HTTPException(403,"Administrator required")
    if scope == "read" and role == "sensor":
        raise HTTPException(403,"Sensor cannot read records")
    configured = os.getenv("PORINI_TENANT_ID", "demo-conservancy")
    if tenant != configured:
        raise HTTPException(403,"Tenant outside API-key scope")

def bind_roles(role_dependency):
    @router.post("/records",status_code=201)
    def create_record(record: ConservationRecord, role: str = Depends(role_dependency)):
        _authorize(record.tenant,role,"write")
        if role == "sensor" and record.status != "unverified":
            raise HTTPException(403,"Device submissions require verification")
        identifier = str(uuid4())
        data = record.model_dump(mode="json")
        if data["observed_at"].endswith("+00:00") is False and record.observed_at.tzinfo is None:
            raise HTTPException(422,"Timezone required")
        with _lock, connection() as db:
            db.execute("INSERT INTO records VALUES (?,?,?,?,?)",(identifier,record.tenant,record.kind,
                       datetime.now(timezone.utc).isoformat(),json.dumps(data)))
        return {"id":identifier,**data}

    @router.get("/records")
    def list_records(kind: str | None = None, limit: int = 100,
                     role: str = Depends(role_dependency)):
        tenant = os.getenv("PORINI_TENANT_ID","demo-conservancy")
        _authorize(tenant,role,"read")
        if not 1 <= limit <= 500:
            raise HTTPException(422,"limit must be 1..500")
        query = "SELECT id,payload FROM records WHERE tenant=?"
        args = [tenant]
        if kind:
            query += " AND kind=?"
            args.append(kind)
        query += " ORDER BY created DESC LIMIT ?"
        args.append(limit)
        with _lock, connection() as db:
            rows = db.execute(query,args).fetchall()
        # Return full data only to authorized team, never public mapping.
        return [{"id":i,**json.loads(p)} for i,p in rows]

    @router.post("/records/{record_id}/review")
    def review_record(record_id: str, review: Review, role: str = Depends(role_dependency)):
        tenant = os.getenv("PORINI_TENANT_ID","demo-conservancy")
        _authorize(tenant,role,"review")
        with _lock, connection() as db:
            row = db.execute("SELECT payload FROM records WHERE id=? AND tenant=?",(record_id,tenant)).fetchone()
            if not row:
                raise HTTPException(404,"Record not found")
            payload = json.loads(row[0])
            payload["status"]=review.status
            payload["review"] = review.model_dump()
            db.execute("UPDATE records SET payload=? WHERE id=?",(json.dumps(payload),record_id))
        return {"id":record_id,**payload}

    @router.get("/geojson")
    def geojson(kind: str | None = None, role: str = Depends(role_dependency)):
        records = list_records(kind=kind,limit=500,role=role)
        features=[]
        for entry in records:
            if entry.get("latitude") is None or entry.get("longitude") is None: continue
            properties={k:v for k,v in entry.items() if k not in ("latitude","longitude","metadata")}
            features.append({"type":"Feature","geometry":{"type":"Point","coordinates":[entry["longitude"],entry["latitude"]]},"properties":properties})
        return {"type":"FeatureCollection","features":features}

    @router.get("/biodiversity/summary")
    def biodiversity_summary(role: str = Depends(role_dependency)):
        observations = list_records(kind="species_sighting",limit=500,role=role)
        validated=[x for x in observations if x["status"]=="verified" and not x["synthetic"]]
        totals={}
        for item in validated:
            species=item.get("metadata",{}).get("species")
            if species:
                totals[species]=totals.get(species,0)+1
        return {"verified_real_sightings":len(validated),"observations_by_species":totals,
                "warning":"Counts are detections, not population estimates. Duplicate individuals possible."}
    return router
