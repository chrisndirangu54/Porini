"""FireShield hybrid-agent advisory. Never authorizes release, flight, or actuation."""
from dataclasses import dataclass

@dataclass(frozen=True)
class WildfireScenario:
    fire_verified: bool = False
    sensor_fresh: bool = False
    incident_command_approved: bool = False
    people_clear: bool = False
    wildlife_clear: bool = False
    wind_mps: float = 0.0
    near_waterway: bool = False
    chemical_ecology_reviewed: bool = False

def hybrid_agent_advisory(s: WildfireScenario) -> dict:
    warnings = []
    if not s.fire_verified: warnings.append("Fire not independently verified")
    if not s.sensor_fresh: warnings.append("Sensor observations stale or absent")
    if not s.incident_command_approved: warnings.append("Incident-command approval absent")
    if not s.people_clear: warnings.append("People clearance unverified")
    if not s.wildlife_clear: warnings.append("Wildlife clearance unverified")
    if s.wind_mps >= 6: warnings.append("Elevated spray drift risk")
    if s.near_waterway: warnings.append("Chemical-agent application restricted near waterways")
    if not s.chemical_ecology_reviewed: warnings.append("Retardant/foam ecological review incomplete")
    return {
        "candidate_modes": [
            {"name": "water cooling", "type": "liquid", "status": "advisory_only"},
            {"name": "approved long-term vegetation retardant", "type": "liquid", "status": "requires_ecological_review"},
            {"name": "approved Class A wetting agent", "type": "liquid", "status": "requires_ecological_review"}
        ],
        "excluded_modes": ["chemically generated gas capsules", "dropped compressed-gas munitions", "outdoor oxygen-displacement gas clouds"],
        "simulation_ready": not warnings,
        "warnings": warnings,
        "physical_release_enabled": False,
        "actuator_command": None,
        "note": "Advisory simulation only. No automatic drone dispatch or suppressant deployment."
    }
