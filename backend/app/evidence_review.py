"""Minimal evidence manifest + independent human-label review.

Stores hashes and metadata only; no raw media, biometric IDs or secrets.
Deployment requires an encrypted evidence store and stronger auth.
"""
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException

class EvidenceManifestIn(BaseModel):
    incident_id: str = Field(min_length=3, max_length=120)
    sensor_id: str = Field(min_length=2, max_length=120)
    media_type: str = Field(pattern=r"^(image/jpeg|image/png|audio/wav|application/octet-stream)$")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bytes_size: int = Field(gt=0, le=500_000_000)
    capture_time: datetime
    synthetic: bool = True
    model_version: str | None = Field(default=None, max_length=100)

class ReviewIn(BaseModel):
    label: str = Field(min_length=2, max_length=100)
    confirmed: bool
    reviewer_id: str = Field(min_length=2, max_length=120)
    note: str = Field(default="", max_length=1000)

def bind_evidence(store, allowed_role):
    router = APIRouter(prefix="/evidence", tags=["Evidence review"])
    path = os.getenv("PORINI_CORE_DB_PATH", "/tmp/porini_core.sqlite3")
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS evidence_manifest (
            id TEXT PRIMARY KEY, incident_id TEXT NOT NULL, record_json TEXT NOT NULL)""")
        db.execute("""CREATE TABLE IF NOT EXISTS evidence_review (
            id TEXT PRIMARY KEY, manifest_id TEXT NOT NULL, record_json TEXT NOT NULL)""")

    @router.post("/manifests", status_code=201)
    def register(item: EvidenceManifestIn, role=Depends(allowed_role("admin", "ranger"))):
        if item.incident_id not in store.incidents:
            raise HTTPException(404, "Incident not found")
        record = {"id": str(uuid4()), **item.model_dump(mode="json"),
                  "registered_at": datetime.now(timezone.utc).isoformat(),
                  "storage_status": "metadata_only_no_media_uploaded"}
        with sqlite3.connect(path) as db:
            db.execute("INSERT INTO evidence_manifest VALUES(?,?,?)",
                       (record["id"], item.incident_id, json.dumps(record)))
        store.log("evidence.manifest_registered", role,
                  {"id": record["id"], "incident_id": item.incident_id})
        return record

    @router.get("/incidents/{incident_id}")
    def list_for_incident(incident_id: str, role=Depends(allowed_role("admin", "ranger"))):
        if incident_id not in store.incidents:
            raise HTTPException(404, "Incident not found")
        with sqlite3.connect(path) as db:
            records = db.execute("SELECT record_json FROM evidence_manifest WHERE incident_id=?", (incident_id,)).fetchall()
        return [json.loads(row[0]) for row in records]

    @router.post("/{manifest_id}/reviews", status_code=201)
    def review(manifest_id: str, item: ReviewIn, role=Depends(allowed_role("admin", "ranger"))):
        with sqlite3.connect(path) as db:
            exists = db.execute("SELECT id FROM evidence_manifest WHERE id=?", (manifest_id,)).fetchone()
            if not exists:
                raise HTTPException(404, "Manifest not found")
            result = {"id": str(uuid4()), "manifest_id": manifest_id,
                      **item.model_dump(), "reviewed_at": datetime.now(timezone.utc).isoformat()}
            db.execute("INSERT INTO evidence_review VALUES(?,?,?)",
                       (result["id"], manifest_id, json.dumps(result)))
        store.log("evidence.reviewed", role, {"manifest_id": manifest_id, "review_id": result["id"]})
        return result

    @router.get("/{manifest_id}/reviews")
    def reviews(manifest_id: str, role=Depends(allowed_role("admin", "ranger"))):
        with sqlite3.connect(path) as db:
            rows = db.execute("SELECT record_json FROM evidence_review WHERE manifest_id=?", (manifest_id,)).fetchall()
        return [json.loads(r[0]) for r in rows]
    return router
