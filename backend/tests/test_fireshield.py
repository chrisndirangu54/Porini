from types import SimpleNamespace
import pytest
from app.fireshield import assess, FIRE_EVENT_TYPES

def sample(**changes):
    obj = dict(id="inc-1",event_type="possible_wildfire",priority="P2",
               confidence=0.55,uncertainty_m=800,synthetic=True)
    obj.update(changes)
    return SimpleNamespace(**obj)

def test_assessment_requires_verification_and_never_authorizes_release():
    result = assess(sample())
    assert result.verification == "requires_human_verification"
    assert result.suppression_authorized is False
    assert result.synthetic is True
    assert any("additional observations" in x for x in result.options)
    assert any("No autonomous" in x for x in result.cautions)

def test_non_fire_rejected():
    with pytest.raises(ValueError):
        assess(sample(event_type="possible_gunshot"))

def test_recognized_fire_types():
    assert "smoke_detected" in FIRE_EVENT_TYPES
