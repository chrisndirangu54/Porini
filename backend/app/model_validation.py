"""Independent site-holdout evaluation of precomputed detector outputs.

No trained models are bundled. Never train/calibrate on the held-out sites.
Labels must come from verified independent field review.
"""
from collections import defaultdict
from pydantic import BaseModel, Field, model_validator
from typing import Literal

class ReviewedPrediction(BaseModel):
    sample_id: str = Field(min_length=1)
    site_id: str = Field(min_length=1)
    modality: Literal["optical","thermal","infrared","acoustic"]
    target: Literal["fire","smoke","chainsaw","gunshot"]
    split: Literal["train","validation","test"]
    weather: str = Field(min_length=1)
    light: Literal["day","night","twilight"]
    model_version: str = Field(min_length=1)
    score: float = Field(ge=0,le=1)
    verified_label: bool
    reviewer_id: str = Field(min_length=2)
    verified: bool = True
    @model_validator(mode="after")
    def reviewed(self):
        if not self.verified:
            raise ValueError("Independent evaluation requires verified human labels")
        return self

def evaluate(records: list[ReviewedPrediction], threshold: float = 0.5) -> dict:
    if not 0 < threshold < 1:
        raise ValueError("Threshold must be predetermined within (0,1)")
    if not records:
        raise ValueError("No reviewed predictions supplied")
    ids = [r.sample_id for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate sample IDs")
    # Site-level partitioning prevents nearby recordings leaking across splits.
    sites = defaultdict(set)
    for r in records:
        sites[r.site_id].add(r.split)
    if any(len(splits)>1 for splits in sites.values()):
        raise ValueError("Site leakage across train/validation/test")
    versions = {r.model_version for r in records}
    if len(versions)!=1:
        raise ValueError("Do not mix model versions in one report")
    held = [r for r in records if r.split=="test"]
    if not held:
        raise ValueError("No independent test sites")
    def summarize(items):
        tp=sum(r.score>=threshold and r.verified_label for r in items)
        fp=sum(r.score>=threshold and not r.verified_label for r in items)
        fn=sum(r.score<threshold and r.verified_label for r in items)
        tn=sum(r.score<threshold and not r.verified_label for r in items)
        safe=lambda x,d: round(x/d,4) if d else None
        return {"n":len(items),"tp":tp,"fp":fp,"fn":fn,"tn":tn,
                "precision":safe(tp,tp+fp),"recall":safe(tp,tp+fn),
                "specificity":safe(tn,tn+fp),"f1":safe(2*tp,2*tp+fp+fn)}
    groups=defaultdict(list)
    for r in held:
        for kind,key in (("site",r.site_id),("modality",r.modality),("target",r.target),
                         ("weather",r.weather),("light",r.light)):
            groups[kind+":"+key].append(r)
    return {"model_version":held[0].model_version,"threshold":threshold,
            "test_sites":len({r.site_id for r in held}),"overall":summarize(held),
            "strata":{key:summarize(value) for key,value in sorted(groups.items())},
            "warning":"Retrospective classification metrics only. No deployment approval implied. False alarms per sensor-day and detection latency require exposure/time metadata."}
