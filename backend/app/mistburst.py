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
MODES = ("MistBurst-W", "MistBurst-G", "MistBurst-R", "flush")
class CompatibilityReview(BaseModel):
    formulation: Literal["MistBurst-W", "MistBurst-G", "MistBurst-R"]
    application: Literal["hotspot", "temporary_vegetation_protection", "fireline"]
    product_approved: bool = False
    nozzle_compatible: bool = False
    environmental_clearance: bool = False
    operator_reviewed: bool = False

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
    return {"formulation": req.formulation, "application": req.application,
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
    @router.post("/compatibility-review")
    def compatibility(request: CompatibilityReview, role=Depends(allowed_role("admin", "ranger"))):
        return review(request)
    return router
