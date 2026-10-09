from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.models import EventIn
from app.engine import priority, distance_m
from app.store import MemoryStore

client = TestClient(app)
HEAD = {"X-API-Key": "local-dev-key"}

def test_priority_does_not_confuse_confidence():
    assert priority(5, "possible_gunshot") == "P1"
    assert priority(1, "rare_species_seen") == "P4"

def test_distance():
    assert distance_m(-1, 36, -1, 36) == 0
    assert distance_m(-1, 36, -1.01, 36) > 1000

def test_invalid_coordinates_rejected():
    data = {"source_id":"mic-1","modality":"acoustic","event_type":"chainsaw","latitude":200,"longitude":36,"confidence":.8,"severity":4}
    assert client.post("/events", json=data, headers=HEAD).status_code == 422

def test_auth_and_dedup():
    event = {"source_id":"mic-tests","modality":"acoustic","event_type":"chainsaw","latitude":-1.1,"longitude":37.1,"confidence":.8,"severity":4,"external_id":"ext-001","synthetic":True}
    assert client.get("/incidents").status_code == 401
    one = client.post("/events",json=event,headers=HEAD)
    two = client.post("/events",json=event,headers=HEAD)
    assert one.status_code == 201
    assert one.json()["id"] == two.json()["id"]

def test_approve_request_requires_admin():
    event = client.post("/events",headers=HEAD,json={"source_id":"thermal-9","modality":"thermal","event_type":"animal_distress","latitude":-1.5,"longitude":37.0,"confidence":.6,"severity":4}).json()
    incident_id = event["incident_id"]
    request = client.post(f"/incidents/{incident_id}/drone-requests",headers=HEAD,json={"drone_id":"drone-alpha","purpose":"Non-confrontational observation"}).json()
    assert request["state"] == "pending_human_approval"
    assert request["flight_executed"] is False
    result = client.post(f"/missions/{request['id']}/decision",headers=HEAD,json={"approver_id":"test-admin","approved":True}).json()
    assert result["state"] == "approved_for_operator_review"
    assert result["flight_executed"] is False
