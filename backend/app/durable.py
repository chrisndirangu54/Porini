"""SQLite-backed incident store. Single-process deployment; migrate to PostGIS for scale."""
import json, os, sqlite3, threading
from .store import MemoryStore
from .models import Event, Incident

class DurableStore(MemoryStore):
    def __init__(self,path=None):
        super().__init__()
        self.path=path or os.getenv("PORINI_CORE_DB_PATH","/tmp/porini_core.sqlite3")
        self.lock=threading.RLock()
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.reload()
    def _db(self):
        db=sqlite3.connect(self.path,timeout=20)
        db.execute("PRAGMA journal_mode=WAL")
        return db
    def reload(self):
        with self.lock,self._db() as db:
            data=dict(db.execute("SELECT key,value FROM state"))
        self.events={x["id"]:Event.model_validate(x) for x in json.loads(data.get("events","[]"))}
        self.incidents={x["id"]:Incident.model_validate(x) for x in json.loads(data.get("incidents","[]"))}
        self.assignments=json.loads(data.get("assignments","[]"))
        self.missions={x["id"]:x for x in json.loads(data.get("missions","[]"))}
        self.audit=json.loads(data.get("audit","[]"))
        self.dedup={(e.source_id,e.external_id):e.id for e in self.events.values() if e.external_id}
    def persist(self):
        with self.lock,self._db() as db:
            values={"events":[x.model_dump(mode="json") for x in self.events.values()],
                    "incidents":[x.model_dump(mode="json") for x in self.incidents.values()],
                    "assignments":self.assignments,"missions":list(self.missions.values()),"audit":self.audit}
            db.executemany("INSERT INTO state(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                           [(k,json.dumps(v)) for k,v in values.items()])
    def log(self,action,actor,details):
        super().log(action,actor,details)
        self.persist()
    def ingest(self,payload):
        with self.lock:
            return super().ingest(payload)
