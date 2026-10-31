"""FireShield: advisory wildfire triage. No actuation, release, or flight-control endpoints."""
from datetime import datetime, timezone
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

FIRE_EVENT_TYPES = frozenset({
    "wildfire", "possible_wildfire", "smoke_detected", "fire_detected",
    "thermal_fire_anomaly", "vegetation_fire", "bushfire"
})

class FireAssessment(BaseModel):
    incident_id: str
    event_type: str
    priority: str
    confidence: float
    uncertainty_m: float
    synthetic: bool
    verification: Literal["requires_human_verification"] = "requires_human_verification"
    suppression_authorized: bool = False
    options: list[str]
    cautions: list[str]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

def assess(incident: object) -> FireAssessment:
    """Create conservative non-operational recommendations from existing incident fields."""
    if incident.event_type.lower() not in FIRE_EVENT_TYPES:
        raise ValueError("Incident is not classified as a fire event")
    options = [
        "Request ranger verification and contact the responsible fire authority",
        "Review satellite, thermal, and eyewitness evidence before declaring a confirmed fire",
        "Map safe access, evacuation routes, wildlife exposure, and protected habitats",
        "Review water mist for localized cooling where qualified responders consider it suitable",
        "Review approved water-enhancing firefighting gel for temporary fuel protection",
        "Review approved long-term wildfire retardant for fireline protection where permitted",
        "Restrict FK-5-1-12 to simulated research or specialist enclosed-equipment evaluation; not open vegetation",
    ]
    cautions = [
        "This is decision support, not a confirmed diagnosis or dispatch order",
        "No autonomous drone flight, capsule release, or chemical gas generation is authorized",
        "Gas-based oxygen displacement is unreliable outdoors and hazardous near people or animals",
        "Assess weather, wind, airspace permissions, human exposure, wildlife, and ecological impacts",
    ]
    if incident.confidence < 0.7 or incident.uncertainty_m > 500:
        options.insert(0, "Collect additional observations: detection confidence or location precision is limited")
    return FireAssessment(
        incident_id=incident.id, event_type=incident.event_type,
        priority=incident.priority, confidence=incident.confidence,
        uncertainty_m=incident.uncertainty_m, synthetic=incident.synthetic,
        options=options, cautions=cautions,
    )


# Advisory-only catalog. Do not interpret suitability as a discharge authorization.
SUPPRESSION_AGENTS = [
    {"id": "fk_5_1_12", "name": "FK-5-1-12 vapour", "mechanism": "Heat absorption",
     "vegetation_use": "not_recommended", "enclosed_equipment_use": "specialist_review",
     "persistence": "Disperses in outdoor airflow despite high vapour density",
     "hazards": ["Outdoor effectiveness unverified", "Heat decomposition products", "Exposure and environmental review required"],
     "control": "simulation_only"},
    {"id": "water_mist", "name": "Water mist", "mechanism": "Cooling and localized steam generation",
     "vegetation_use": "conditional", "enclosed_equipment_use": "application_specific",
     "persistence": "Droplets evaporate or drift with wind; coverage depends on delivery",
     "hazards": ["Wind drift", "Insufficient penetration or cooling", "Electrical hazards require rated equipment"],
     "control": "human_review_only"},
    {"id": "firefighting_gel", "name": "Firefighting gel / water enhancer", "mechanism": "Adherent water-based cooling and temporary coating",
     "vegetation_use": "conditional", "enclosed_equipment_use": "application_specific",
     "persistence": "Protective effect declines as water evaporates",
     "hazards": ["Product-specific toxicity and aquatic impacts", "Application and compatibility limits"],
     "control": "human_review_only"},
    {"id": "long_term_retardant", "name": "Long-term wildfire retardant", "mechanism": "Chemical inhibition of vegetation combustion",
     "vegetation_use": "conditional", "enclosed_equipment_use": "not_recommended",
     "persistence": "Some products remain effective after drying",
     "hazards": ["Waterway exclusion zones", "Ecological impacts", "Local authority and product approvals required"],
     "control": "human_review_only"},
]

def bind_fireshield(store, allowed_role):
    router = APIRouter(prefix="/fireshield", tags=["FireShield"])
    @router.get("/suppression-agents")
    def suppression_agents(role=Depends(allowed_role("admin", "ranger"))):
        return {"prototype": True, "physical_actuation_enabled": False,
                "warning": "Advisory comparison only. Outdoor gas blanketing is not an approved deployment mode.",
                "agents": SUPPRESSION_AGENTS}

    @router.get("/incidents", response_model=list[FireAssessment])
    def fire_incidents(role=Depends(allowed_role("admin", "ranger"))):
        return [assess(item) for item in store.incidents.values()
                if item.event_type.lower() in FIRE_EVENT_TYPES]
    @router.get("/incidents/{incident_id}", response_model=FireAssessment)
    def fire_assessment(incident_id: str, role=Depends(allowed_role("admin", "ranger"))):
        item = store.incidents.get(incident_id)
        if item is None:
            raise HTTPException(404, "Incident not found")
        if item.event_type.lower() not in FIRE_EVENT_TYPES:
            raise HTTPException(422, "Incident is not classified as a fire event")
        return assess(item)
    return router
