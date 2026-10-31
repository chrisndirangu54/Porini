from backend.app.review_queue import ReviewQueue
import pytest

def test_tenant_isolation_and_one_time_decision(tmp_path):
    q=ReviewQueue(str(tmp_path/"reviews.db"))
    r=q.enqueue("a","ev-1",{"model":"speciesnet","synthetic":True})
    assert len(q.list("a"))==1 and q.list("b")==[]
    with pytest.raises(ValueError):q.decide("b",r["id"],"ranger-1","confirmed")
    out=q.decide("a",r["id"],"ranger-1","confirmed")
    assert out["status"]=="confirmed" and not out["automatic_enforcement"]
    with pytest.raises(ValueError):q.decide("a",r["id"],"ranger-1","rejected")
