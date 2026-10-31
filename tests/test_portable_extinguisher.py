from backend.app.portable_extinguisher import PortableReview, evaluate_portable

def test_portable_defaults_blocked():
    r=evaluate_portable(PortableReview(agent="water_mist"))
    assert not r["advisory_review_complete"]
    assert r["actuator_command"] is None
    assert r["physical_release_enabled"] is False

def test_outdoor_co2_not_recommended_even_when_reviewed():
    r=evaluate_portable(PortableReview("co2",True,True,True,True,True,True,True))
    assert not r["advisory_review_complete"]
    assert "outdoor_gas_inappropriate" in r["blocked_checks"]
