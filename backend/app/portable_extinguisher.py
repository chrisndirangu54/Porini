"""FireShield portable extinguisher comparison for ranger decision support.

No physical drone, flight, pressure-vessel or extinguisher actuator controls.
"""
from dataclasses import dataclass
from datetime import datetime, timezone

CATALOG = {
 "water_mist":{"use":"Candidate for small surface ignitions when product rated","risk":"Limited payload; drift, cooling and electrical suitability"},
 "abc_dry_chemical":{"use":"Potential small localized multi-class fires where rated","risk":"Wind drift, visibility loss, residue and environmental contamination"},
 "clean_agent":{"use":"Enclosed equipment hazard review only","risk":"Poor outdoor retention and exposure risks"},
 "co2":{"use":"Enclosed equipment hazard review only","risk":"Rapid outdoor dispersion, oxygen displacement and discharge recoil"}
}
@dataclass(frozen=True)
class PortableReview:
    agent:str
    incident_approved:bool=False
    fire_verified:bool=False
    evidence_fresh:bool=False
    wildlife_and_people_clear:bool=False
    environmental_approval:bool=False
    wind_reviewed:bool=False
    certified_product:bool=False

def evaluate_portable(s:PortableReview)->dict:
    if s.agent not in CATALOG: raise ValueError("Unsupported extinguisher agent")
    checks={
      "incident_approved":s.incident_approved,
      "fire_verified":s.fire_verified,
      "evidence_fresh":s.evidence_fresh,
      "wildlife_and_people_clear":s.wildlife_and_people_clear,
      "environmental_approval":s.environmental_approval,
      "wind_reviewed":s.wind_reviewed,
      "certified_product":s.certified_product
    }
    outdoor_gas=s.agent in ("co2","clean_agent")
    return {
      "agent":s.agent,"profile":CATALOG[s.agent],
      "timestamp":datetime.now(timezone.utc).isoformat(),
      "advisory_review_complete":all(checks.values()) and not outdoor_gas,
      "blocked_checks":[k for k,v in checks.items() if not v]+(["outdoor_gas_inappropriate"] if outdoor_gas else []),
      "checks":checks,"physical_release_enabled":False,"actuator_command":None,
      "note":"For qualified response planning only. No drop, drone flight, valve or discharge control."
    }
