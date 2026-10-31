import pytest
from pydantic import ValidationError
from app.mistburst_benchmarks import Trial, TrialComparison, compare_trials

def example(**changes):
    data=dict(propulsion="mechanical_pump", formulation="MistBurst-W", test_id="bench-001",
              discharged_liters=2, electrical_energy_wh=20, gas_recharge_energy_wh=0,
              mass_kg=3, deposited_liters=1.5, coverage_m2=6)
    data.update(changes)
    return data

def test_observed_metrics_and_no_actuation():
    row=compare_trials(TrialComparison(trials=[Trial(**example())]))["results"][0]
    assert row["energy_wh_per_liter"] == 10
    assert row["deposition_fraction"] == 0.75
    assert row["coverage_m2_per_liter"] == 3
    assert row["droplet_dv50_microns"] is None

def test_gas_compression_energy_is_counted():
    row=compare_trials(TrialComparison(trials=[Trial(**example(
        propulsion="compressed_nitrogen", electrical_energy_wh=0,
        gas_recharge_energy_wh=40))]))["results"][0]
    assert row["energy_wh_per_liter"] == 20

def test_no_false_precision_with_zero_deposition():
    row=compare_trials(TrialComparison(trials=[Trial(**example(deposited_liters=0))]))["results"][0]
    assert row["energy_wh_per_deposited_liter"] is None

def test_mass_balance_rejects_impossible_deposition():
    with pytest.raises(ValidationError):
        Trial(**example(deposited_liters=3))

def test_no_unjustified_ranking():
    output=compare_trials(TrialComparison(trials=[Trial(**example())]))
    assert output["ranking"]=="not_computed_without_identical_test_conditions"
    assert output["physical_actuation_enabled"] is False
