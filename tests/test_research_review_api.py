from fastapi.testclient import TestClient
from backend.app.main import app
client=TestClient(app)

def test_review_endpoint_requires_authentication():
    assert client.get("/research/reviews").status_code==401

def test_review_endpoint_fails_closed_without_configuration(monkeypatch):
    monkeypatch.delenv("PORINI_REVIEW_DB",raising=False)
    monkeypatch.delenv("PORINI_TENANT_ID",raising=False)
    key=__import__("os").getenv("PORINI_API_KEY","local-dev-key")
    assert client.get("/research/reviews",headers={"X-API-Key":key}).status_code==503

def test_review_decisions_disabled_without_identity(monkeypatch,tmp_path):
    monkeypatch.setenv("PORINI_REVIEW_DB",str(tmp_path/"reviews.sqlite"))
    monkeypatch.setenv("PORINI_TENANT_ID","test")
    key=__import__("os").getenv("PORINI_API_KEY","local-dev-key")
    res=client.post("/research/reviews/id/decision",headers={"X-API-Key":key},
        json={"reviewer_id":"someone","decision":"confirmed"})
    assert res.status_code==503
