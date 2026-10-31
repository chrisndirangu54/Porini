import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
from app.evidence_review import EvidenceManifestIn, ReviewIn

def test_hash_and_size_validation():
    good=dict(incident_id="incident123",sensor_id="sensor123",media_type="image/jpeg",
      sha256="a"*64,bytes_size=234,capture_time=datetime.now(timezone.utc))
    assert EvidenceManifestIn(**good).synthetic
    with pytest.raises(ValidationError):
        EvidenceManifestIn(**{**good,"sha256":"bad"})
    with pytest.raises(ValidationError):
        EvidenceManifestIn(**{**good,"bytes_size":-3})

def test_review_requires_explicit_verdict():
    assert ReviewIn(label="smoke",confirmed=False,reviewer_id="ranger-01").confirmed is False
    with pytest.raises(ValidationError):
        ReviewIn(label="smoke",reviewer_id="ranger-01")
