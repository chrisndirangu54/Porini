"""Advisory-only gas suppression catalog. No dosing, actuation or chemical generation."""
from typing import Literal
from pydantic import BaseModel

GAS_AGENTS = {
 "co2": {"name":"Carbon dioxide","method":"oxygen_displacement","occupancy":"unoccupied_only","environment":"engineered_enclosure","warning":"Potentially fatal asphyxiation; Class A fuels may reignite"},
 "ig01": {"name":"Argon (IG-01)","method":"oxygen_displacement","occupancy":"engineered_restricted","environment":"engineered_enclosure","warning":"Oxygen depletion hazard; flooding requires certified engineering"},
 "ig541": {"name":"Inergen (IG-541)","method":"oxygen_reduction","occupancy":"engineered_restricted","environment":"engineered_enclosure","warning":"Occupant safety and exposure must be professionally assessed"},
 "fk5112": {"name":"FK-5-1-12","method":"heat_absorption","occupancy":"engineered_restricted","environment":"engineered_enclosure","warning":"Thermal decomposition/exposure and environmental restrictions require assessment"},
 "hfc227ea": {"name":"HFC-227ea","method":"heat_absorption","occupancy":"engineered_restricted","environment":"engineered_enclosure","warning":"Greenhouse-gas restrictions, exposure and decomposition concerns"},
}
class GasReview(BaseModel):
 agent: Literal["co2","ig01","ig541","fk5112","hfc227ea"]
 location: Literal["outdoor_vegetation","occupied_room","unoccupied_enclosure"]
 certified_design: bool=False
 authority_approval: bool=False

def review_gas(req:GasReview)->dict:
    reasons=[]
    if req.location=="outdoor_vegetation":reasons.append("Gas flooding ineffective outdoors; potentially harmful to wildlife")
    if req.location=="occupied_room":reasons.append("No automatic gas selection for occupied rooms; specialist exposure assessment required")
    if req.agent=="co2" and req.location!="unoccupied_enclosure":reasons.append("CO2 flooding prohibited in this advisory workflow where occupancy cannot be excluded")
    if not req.certified_design:reasons.append("Certified design not verified")
    if not req.authority_approval:reasons.append("Authority approval not verified")
    return {"agent":req.agent,"location":req.location,"advisory_review_complete":not reasons,
            "reasons":reasons,"physical_actuation_enabled":False,"release_authorized":False}
