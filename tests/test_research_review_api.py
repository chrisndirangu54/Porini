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
    assert res.status_code==403

def test_oidc_review_uses_verified_claims(monkeypatch,tmp_path):
    import backend.app.main as main
    from backend.app.oidc import verified_claims
    monkeypatch.setenv("PORINI_REVIEW_DB",str(tmp_path/"r.sqlite"))
    monkeypatch.setenv("PORINI_TENANT_ID","conservancy-a")
    monkeypatch.setenv("PORINI_AUTH_MODE","oidc")
    def fake_claims(authorization):
        assert authorization == "Bearer test-token"
        return {"sub":"ranger-from-token","tenant_id":"conservancy-a","roles":["porini:ranger"]}
    monkeypatch.setattr("backend.app.research_review_api.verified_claims",fake_claims)
    # FastAPI's dependency still verifies a real token; override only in this isolated test.
    main.app.dependency_overrides[main.auth]=lambda:"ranger"
    try:
        headers={"Authorization":"Bearer test-token"}
        create=client.post("/research/reviews",headers=headers,json={"evidence_id":"ev-4","candidate":{"model":"speciesnet"}})
        assert create.status_code==200
        rid=create.json()["id"]
        decision=client.post(f"/research/reviews/{rid}/decision",headers=headers,
                    json={"reviewer_id":"spoofed-client-id","decision":"confirmed"})
        assert decision.status_code==200
        assert decision.json()["reviewer_id"]=="ranger-from-token"
    finally:
        main.app.dependency_overrides.clear()
