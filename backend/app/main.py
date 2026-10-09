import os
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from .models import EventIn, StatusUpdate, AssignmentIn, DroneRequestIn, ApprovalIn
from .store import store
from .extensions import bind_roles

app = FastAPI(title="Porini Conservation API", version="0.1.0")
allowed = os.getenv("PORINI_CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=allowed, allow_methods=["GET","POST","PATCH"], allow_headers=["X-API-Key","Content-Type"])
KEY = os.getenv("PORINI_API_KEY", "local-dev-key")
ROLE_KEYS = {KEY: "admin"}
if os.getenv("PORINI_RANGER_KEY"):
    ROLE_KEYS[os.environ["PORINI_RANGER_KEY"]] = "ranger"
if os.getenv("PORINI_SENSOR_KEY"):
    ROLE_KEYS[os.environ["PORINI_SENSOR_KEY"]] = "sensor"

def auth(x_api_key: str | None = Header(None)):
    if x_api_key not in ROLE_KEYS:
        raise HTTPException(401, "Invalid API key")
    return ROLE_KEYS[x_api_key]

def allowed_role(*roles):
    def check(role: str = Depends(auth)):
        if role not in roles:
            raise HTTPException(403, "Insufficient role")
        return role
    return check

@app.get("/health")
def health():
    return {"status": "ok", "prototype": True, "persistence": "memory"}

@app.get("/overview")
def overview(role=Depends(allowed_role("admin", "ranger"))):
    items = list(store.incidents.values())
    return {"incidents": len(items), "active": sum(x.status != "resolved" for x in items),
            "critical": sum(x.priority == "P1" and x.status != "resolved" for x in items),
            "events": len(store.events), "synthetic": sum(x.synthetic for x in items),
            "missions": len(store.missions), "assignments": len(store.assignments)}

@app.get("/incidents")
def incidents(role=Depends(allowed_role("admin", "ranger"))):
    return sorted(store.incidents.values(), key=lambda x: x.updated_at, reverse=True)

@app.get("/incidents/{incident_id}")
def incident(incident_id: str, role=Depends(allowed_role("admin", "ranger"))):
    if incident_id not in store.incidents:
        raise HTTPException(404, "Incident not found")
    return store.incidents[incident_id]

@app.get("/events")
def events(role=Depends(allowed_role("admin", "ranger"))):
    return sorted(store.events.values(), key=lambda x: x.timestamp, reverse=True)

@app.post("/events", status_code=201)
def ingest(event: EventIn, role=Depends(allowed_role("admin", "sensor"))):
    return store.ingest(event)

@app.patch("/incidents/{incident_id}/status")
def set_status(incident_id: str, update: StatusUpdate, role=Depends(allowed_role("admin", "ranger"))):
    obj = store.incidents.get(incident_id)
    if not obj:
        raise HTTPException(404, "Incident not found")
    obj.status = update.status
    obj.updated_at = datetime.now(timezone.utc)
    store.log("incident.status", role, {"incident_id": incident_id, "status": update.status})
    return obj

@app.post("/incidents/{incident_id}/assignments", status_code=201)
def assign(incident_id: str, assignment: AssignmentIn, role=Depends(allowed_role("admin", "ranger"))):
    if incident_id not in store.incidents:
        raise HTTPException(404, "Incident not found")
    item = {"id": str(uuid4()), "incident_id": incident_id, **assignment.model_dump(), "status": "assigned"}
    store.assignments.append(item)
    store.log("ranger.assigned", role, item)
    return item

@app.get("/assignments")
def assignments(role=Depends(allowed_role("admin", "ranger"))):
    return store.assignments

@app.post("/incidents/{incident_id}/drone-requests", status_code=201)
def request_flight(incident_id: str, request: DroneRequestIn, role=Depends(allowed_role("admin", "ranger"))):
    if incident_id not in store.incidents:
        raise HTTPException(404, "Incident not found")
    mission = {"id": str(uuid4()), "incident_id": incident_id, **request.model_dump(),
               "state": "pending_human_approval", "flight_executed": False, "approver_id": None}
    store.missions[mission["id"]] = mission
    store.log("drone.requested", role, {"mission_id": mission["id"]})
    return mission

@app.get("/missions")
def missions(role=Depends(allowed_role("admin", "ranger"))):
    return list(store.missions.values())

@app.post("/missions/{mission_id}/decision")
def mission_decision(mission_id: str, decision: ApprovalIn, role=Depends(allowed_role("admin"))):
    mission = store.missions.get(mission_id)
    if not mission:
        raise HTTPException(404, "Mission not found")
    if mission["state"] != "pending_human_approval":
        raise HTTPException(409, "Mission already decided")
    mission["state"] = "approved_for_operator_review" if decision.approved else "rejected"
    mission["approver_id"] = decision.approver_id
    mission["decision_note"] = decision.note
    store.log("drone.decision", decision.approver_id, {"mission_id": mission_id, "state": mission["state"]})
    return mission

@app.get("/audit")
def audit(role=Depends(allowed_role("admin"))):
    return store.audit

@app.post("/demo/seed")
def seed(role=Depends(allowed_role("admin"))):
    if os.getenv("PORINI_ENABLE_DEMO", "true").lower() != "true":
        raise HTTPException(403, "Demo disabled")
    store.seed_demo()
    return {"events": len(store.events), "synthetic": True}

# Extensible, locally durable conservation science records.
app.include_router(bind_roles(auth))
