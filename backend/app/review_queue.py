"""Durable, tenant-scoped human review queue for conservation model candidates.

SQLite dev implementation. Deploy a managed database with row-level controls in production.
"""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS research_reviews (
 id TEXT PRIMARY KEY,
 tenant_id TEXT NOT NULL,
 evidence_id TEXT NOT NULL,
 candidate_json TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('pending','confirmed','rejected')),
 reviewer_id TEXT,
 note TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL,
 reviewed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_research_reviews_tenant ON research_reviews(tenant_id,status,created_at);
"""

class ReviewQueue:
    def __init__(self, db_path: str):
        self.path=str(Path(db_path))
        with self._connect() as conn: conn.executescript(SCHEMA)

    def _connect(self):
        return sqlite3.connect(self.path, timeout=15)

    def enqueue(self, tenant_id: str, evidence_id: str, candidate: dict)->dict:
        if not tenant_id or not evidence_id: raise ValueError("Missing tenant or evidence ID")
        if not isinstance(candidate,dict) or not candidate: raise ValueError("Missing candidate metadata")
        item_id=str(uuid.uuid4())
        now=datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute("INSERT INTO research_reviews(id,tenant_id,evidence_id,candidate_json,status,created_at) VALUES(?,?,?,?,?,?)",
                         (item_id,tenant_id,evidence_id,json.dumps(candidate,allow_nan=False),"pending",now))
        return {"id":item_id,"status":"pending","evidence_id":evidence_id,"synthetic":bool(candidate.get("synthetic",False))}

    def list(self, tenant_id: str, status: str="pending")->list[dict]:
        if status not in ("pending","confirmed","rejected"):raise ValueError("Invalid status")
        with self._connect() as conn:
            rows=conn.execute("SELECT id,evidence_id,candidate_json,status FROM research_reviews WHERE tenant_id=? AND status=? ORDER BY created_at DESC LIMIT 100",
                              (tenant_id,status)).fetchall()
        return [{"id":r[0],"evidence_id":r[1],"candidate":json.loads(r[2]),"status":r[3]} for r in rows]

    def decide(self,tenant_id:str, review_id:str,reviewer_id:str, decision:str,note:str="")->dict:
        if decision not in ("confirmed","rejected"):raise ValueError("Invalid decision")
        if not reviewer_id or len(note)>1000:raise ValueError("Invalid reviewer or note")
        with self._connect() as conn:
            result=conn.execute("UPDATE research_reviews SET status=?,reviewer_id=?,note=?,reviewed_at=? WHERE tenant_id=? AND id=? AND status='pending'",
               (decision,reviewer_id,note,datetime.now(timezone.utc).isoformat(),tenant_id,review_id))
            if result.rowcount != 1:raise ValueError("Review missing, wrong tenant or already decided")
        return {"id":review_id,"status":decision,"reviewer_id":reviewer_id,"automatic_enforcement":False}
