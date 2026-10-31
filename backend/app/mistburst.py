"""MistBurst advisory formulation catalog and compatibility review.

No chemical recipe, mixture ratios, discharge settings, or hardware actuation.
Use certified product documentation, local permits and qualified fire professionals.
"""
from typing import Literal
from fastapi import APIRouter, Depends
from pydantic import BaseModel

FORMULATIONS = {
    "MistBurst-W": {"name": "Water", "agent_id": "water_mist", "purpose": "Localized cooling", "persistence": "Short; evaporates or drains", "viscosity": "low", "nozzle": "rated_water_mist", "notes": ["Wind drift and inadequate fuel penetration possible"]},
    "MistBurst-G": {"name": "Approved water-enhancer gel", "agent_id": "firefighting_gel", "purpose": "Temporary moisture adhesion on vegetation", "persistence": "Until hydration is lost", "viscosity": "product_dependent", "nozzle": "manufacturer_approved_gel", "notes": ["Check seal, pump, nozzle and environment compatibility against product technical data"]},
    "MistBurst-R": {"name": "Approved long-term wildfire retardant", "agent_id": "long_term_retardant", "purpose": "Strategic fireline protection", "persistence": "May inhibit combustion after drying", "viscosity": "product_dependent", "nozzle": "manufacturer_approved_retardant", "notes": ["Apply waterway and sensitive habitat restrictions", "Follow certified mixing and cleanup instructions"]},
}
PROPELLANTS = {
    "compressed_air": {"name": "Certified compressed air", "type": "stored_gas", "status": "engineering_review",
        "applications": ["MistBurst-W", "MistBurst-G", "MistBurst-R"],
        "cautions": ["Pressure vessel and regulator certification required", "Foaming and spray behavior require formulation-specific testing"]},
    "compressed_nitrogen": {"name": "Certified compressed nitrogen", "type": "stored_gas", "status": "engineering_review",
        "applications": ["MistBurst-W", "MistBurst-G", "MistBurst-R"],
        "cautions": ["Asphyxiation hazard in enclosed areas", "Regulated vessel and nozzle compatibility testing required"]},
    "chemical_gas_generator": {"name": "Chemical gas-generation cartridge (research concept)", "type": "generated_gas",
        "status": "simulation_only", "applications": [],
        "cautions": ["No reaction recipes, gas synthesis or ignition mechanisms permitted",
                     "Thermal runaway, pressure rise, toxic by-products and inadvertent actuation require independent assessment"]},
    "mechanical_pump": {"name": "Electromechanical pump baseline", "type": "non_gas",
        "status": "engineering_review", "applications": ["MistBurst-W", "MistBurst-G", "MistBurst-R"],
        "cautions": ["Pump and nozzle must be rated for formulation viscosity"]},
}
MODES = ("MistBurst-W", "MistBurst-G", "MistBurst-R", "flush")
class CompatibilityReview(BaseModel):
    formulation: Literal["MistBurst-W", "MistBurst-G", "MistBurst-R"]
    application: Literal["hotspot", "temporary_vegetation_protection", "fireline"]
    product_approved: bool = False
    nozzle_compatible: bool = False
    environmental_clearance: bool = False
    operator_reviewed: bool = False
    propellant: Literal["compressed_air", "compressed_nitrogen", "chemical_gas_generator", "mechanical_pump"] = "mechanical_pump"
    vessel_certified: bool = False

def review(req: CompatibilityReview) -> dict:
    allowed = {"hotspot": "MistBurst-W", "temporary_vegetation_protection": "MistBurst-G", "fireline": "MistBurst-R"}
    issues = []
    if req.formulation != allowed[req.application]:
        issues.append("Formulation differs from preferred application; specialist review required")
    for field, message in (
        ("product_approved", "Certified product approval not confirmed"),
        ("nozzle_compatible", "Pump/seal/nozzle compatibility not confirmed"),
        ("environmental_clearance", "Environmental restrictions not cleared"),
        ("operator_reviewed", "Qualified operator review incomplete"),
    ):
        if not getattr(req, field):
            issues.append(message)
    propellant = PROPELLANTS[req.propellant]
    if req.formulation not in propellant["applications"]:
        issues.append("Selected propellant has no validated formulation pathway; simulation only")
    if propellant["type"] == "stored_gas" and not req.vessel_certified:
        issues.append("Certified vessel, regulator and inspection records not confirmed")
    return {"formulation": req.formulation, "application": req.application, "propellant": req.propellant,
            "advisory_ready": not issues, "physical_actuation_enabled": False,
            "authorization": "none", "issues": issues,
            "warning": "Advisory status is not permission to release, mix, fly or operate hardware."}

def bind_mistburst(allowed_role):
    router = APIRouter(prefix="/fireshield/mistburst", tags=["MistBurst"])
    @router.get("/formulations")
    def formulations(role=Depends(allowed_role("admin", "ranger"))):
        return {"formulations": [{"id": key, **value} for key, value in FORMULATIONS.items()],
                "modes": MODES, "shared_hardware": "concept_only",
                "mixing_policy": "Separate cartridges; no gel-retardant premixing without validated manufacturer approval",
                "changeover": "Manufacturer-approved flush and inspection required",
                "physical_actuation_enabled": False}
    @router.get("/propellants")
    def propellants(role=Depends(allowed_role("admin", "ranger"))):
        return {"propellants": [{"id": key, **value} for key, value in PROPELLANTS.items()],
                "physical_actuation_enabled": False,
                "disclaimer": "No chemical generation or compressed-gas actuation is implemented."}

    @router.post("/compatibility-review")
    def compatibility(request: CompatibilityReview, role=Depends(allowed_role("admin", "ranger"))):
        return review(request)
    return router
