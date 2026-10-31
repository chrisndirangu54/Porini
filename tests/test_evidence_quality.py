from datetime import datetime, timedelta, timezone
import pytest
from backend.app.evidence_quality import Evidence, evidence_review, binary_metrics, group_evaluation

def make_evidence(**kw):
    now=datetime(2026,10,31,tzinfo=timezone.utc)
    values=dict(event_id="e1",source="camera-1",model_id="megadetector_v6",
        confidence=.9,observed_at=now,ingested_at=now,synthetic=False,
        location_uncertainty_m=25,verified_by_human=False)
    values.update(kw)
    return Evidence(**values)

def test_human_review_never_equals_automatic_dispatch():
    result=evidence_review(make_evidence())
    assert result["eligible_for_human_review"]
    assert not result["confirmed"] and not result["dispatch_authorized"]

def test_synthetic_and_stale_flagged():
    now=datetime(2026,10,31,tzinfo=timezone.utc)
    r=evidence_review(make_evidence(synthetic=True,observed_at=now-timedelta(hours=3)))
    assert "synthetic_evidence" in r["warnings"]
    assert "stale_observation" in r["warnings"]

def test_future_timestamp_is_flagged():
    now=datetime(2026,10,31,tzinfo=timezone.utc)
    assert "observation_timestamp_after_ingestion" in evidence_review(
        make_evidence(observed_at=now+timedelta(seconds=1)))["warnings"]

def test_metrics():
    m=binary_metrics([1,0,1,0],[.9,.8,.8,.1])
    assert m["tp"]==2 and m["fp"]==1 and m["fn"]==0 and m["tn"]==1
    assert m["recall"]==1 and m["precision"]==2/3
    assert 0<=m["brier_score"]<=1

def test_groups_and_small_sample_warning():
    result=group_evaluation([("wet",1,.8),("dry",0,.1)],minimum_group_size=5)
    assert result["wet"]["group_size_warning"]
    assert set(result)=={"wet","dry"}

def test_invalid_probabilities_rejected():
    with pytest.raises(ValueError):binary_metrics([1],[float("nan")])
