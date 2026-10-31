from app.mistburst import FORMULATIONS, CompatibilityReview, review

def test_separate_modes_and_agents():
    assert set(FORMULATIONS) == {"MistBurst-W", "MistBurst-G", "MistBurst-R"}
    assert len({v["agent_id"] for v in FORMULATIONS.values()}) == 3

def test_incomplete_checks_block_advisory_readiness():
    result = review(CompatibilityReview(formulation="MistBurst-G", application="temporary_vegetation_protection"))
    assert not result["advisory_ready"]
    assert not result["physical_actuation_enabled"]
    assert result["issues"]

def test_complete_checks_still_never_authorize_discharge():
    result = review(CompatibilityReview(
        formulation="MistBurst-R", application="fireline", product_approved=True,
        nozzle_compatible=True, environmental_clearance=True, operator_reviewed=True))
    assert result["advisory_ready"]
    assert result["authorization"] == "none"
    assert result["physical_actuation_enabled"] is False

def test_mismatched_application_requires_review():
    result = review(CompatibilityReview(formulation="MistBurst-W", application="fireline",
        product_approved=True, nozzle_compatible=True, environmental_clearance=True, operator_reviewed=True))
    assert not result["advisory_ready"]
