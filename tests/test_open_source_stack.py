from backend.app.open_source_stack import catalog, validate_selection
def test_license_gate_prevents_automatic_adoption():
    result=validate_selection(["birdnet","megadetector_v6"],[])
    assert set(result["license_review_pending"])=={"birdnet","megadetector_v6"}
    assert result["automatically_installed"] is False
def test_unknown_component_rejected():
    assert not validate_selection(["unknown"],[])["eligible_for_configuration"]
def test_catalog_does_not_claim_deployment():
    assert not catalog()["production_ready"]
