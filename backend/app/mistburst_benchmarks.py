"""Evidence-based bench comparison of MistBurst atomizers (no actuation).

Metrics are computed ONLY from operator-entered laboratory observations.
Unknown or unmeasured values are never filled with guessed performance.
"""
from typing import Literal
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, model_validator

class Trial(BaseModel):
    propulsion: Literal["mechanical_pump", "compressed_air", "compressed_nitrogen"]
    formulation: Literal["MistBurst-W", "MistBurst-G", "MistBurst-R"]
    test_id: str = Field(min_length=1, max_length=80)
    discharged_liters: float = Field(gt=0, le=100000)
    electrical_energy_wh: float = Field(ge=0, le=1e8)
    gas_recharge_energy_wh: float = Field(ge=0, le=1e8)
    mass_kg: float = Field(gt=0, le=1e6)
    deposited_liters: float = Field(ge=0, le=100000)
    coverage_m2: float = Field(ge=0, le=1e8)
    droplet_dv50_microns: float | None = Field(default=None, gt=0, le=100000)
    spray_uniformity_cv: float | None = Field(default=None, ge=0, le=10)
    @model_validator(mode="after")
    def validate_physics(self):
        if self.deposited_liters > self.discharged_liters:
            raise ValueError("Deposited water cannot exceed discharged volume")
        return self

class TrialComparison(BaseModel):
    trials: list[Trial] = Field(min_length=1, max_length=100)

def compare_trials(payload: TrialComparison):
    rows=[]
    for t in payload.trials:
        total_wh=t.electrical_energy_wh+t.gas_recharge_energy_wh
        rows.append({
            "test_id":t.test_id,"propulsion":t.propulsion,"formulation":t.formulation,
            "energy_wh_per_liter":round(total_wh/t.discharged_liters,4),
            "energy_wh_per_deposited_liter":round(total_wh/t.deposited_liters,4) if t.deposited_liters else None,
            "deposition_fraction":round(t.deposited_liters/t.discharged_liters,4),
            "coverage_m2_per_liter":round(t.coverage_m2/t.discharged_liters,4),
            "hardware_mass_kg":t.mass_kg,
            "droplet_dv50_microns":t.droplet_dv50_microns,
            "spray_uniformity_cv":t.spray_uniformity_cv,
        })
    return {"results":rows,"source":"user_supplied_bench_data",
            "ranking":"not_computed_without_identical_test_conditions",
            "physical_actuation_enabled":False,
            "warning":"Measurements are unverified. Include all upstream gas-compression energy; do not compare differing nozzles, formulations or winds as controlled trials."}

def bind_benchmarks(allowed_role):
    router=APIRouter(prefix="/fireshield/mistburst",tags=["MistBurst"])
    @router.post("/benchmarks/compare")
    def compare(payload:TrialComparison,role=Depends(allowed_role("admin","ranger"))):
        return compare_trials(payload)
    return router
