"""Data query and scientifically honest observation adapters."""
import os
from datetime import datetime,timezone
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from .audio import extract_features, impulsive_candidate
from .imagery import STACObservation,validate_scene
from .extensions import connection
router=APIRouter(prefix="/field",tags=["field adapters"])
class AcousticSamples(BaseModel):
    source_id:str=Field(min_length=2)
    sample_rate:int=Field(ge=8000,le=192000)
    samples:list[float]=Field(min_length=1,max_length=192000)
class ConservationBounds(BaseModel):
    west:float=Field(ge=-180,le=180)
    south:float=Field(ge=-90,le=90)
    east:float=Field(ge=-180,le=180)
    north:float=Field(ge=-90,le=90)
class STACSearch(BaseModel):
    catalog_url:str
    collections:list[str]
    bbox:tuple[float,float,float,float]
    limit:int=Field(default=10,ge=1,le=50)
def bind_field(role_dep):
    @router.post("/acoustic/features")
    def acoustic_features(data:AcousticSamples,role=Depends(role_dep)):
        if role not in ("admin","sensor"):raise HTTPException(403,"Not permitted")
        if len(data.samples)>data.sample_rate*10:raise HTTPException(422,"Maximum 10 seconds")
        features=extract_features(data.samples,data.sample_rate)
        return {"source_id":data.source_id,"features":features.__dict__,"assessment":impulsive_candidate(features)}
    @router.post("/satellite/validate")
    def satellite_validate(scene:STACObservation,role=Depends(role_dep)):
        if role not in ("admin","ranger"):raise HTTPException(403,"Not permitted")
        return validate_scene(scene)
    @router.get("/export/observations")
    def observations_export(role=Depends(role_dep)):
        if role not in ("admin","ranger"):raise HTTPException(403,"Not permitted")
        tenant=os.getenv("PORINI_TENANT_ID","demo-conservancy")
        with connection() as db:
            data=db.execute("SELECT id,payload FROM records WHERE tenant=?",(tenant,)).fetchall()
        import json
        features=[]
        for id,p in data:
            rec=json.loads(p)
            if rec.get("latitude") is None or rec.get("longitude") is None:continue
            features.append({"type":"Feature","geometry":{"type":"Point","coordinates":[rec["longitude"],rec["latitude"]]},
                             "properties":{"id":id,"kind":rec["kind"],"synthetic":rec["synthetic"],"status":rec["status"]}})
        return {"type":"FeatureCollection","features":features}
    return router
