"""Porini evidence provenance, freshness and evaluation utilities.

No inferred observation becomes a confirmed wildlife or fire event automatically.
Offline evaluation only; no tracking, dispatch, actuation, or enforcement logic.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Iterable

MODEL_REGISTRY = {
    "megadetector_v6": {
        "task":"animal/person/vehicle detection",
        "provider":"Microsoft AI for Good Lab",
        "model_reference":"https://github.com/microsoft/MegaDetector",
        "runtime":"external_not_installed",
        "note":"Detector only; cannot infer species or criminal intent."
    },
    "speciesnet": {
        "task":"camera-trap species classification",
        "provider":"Google",
        "model_reference":"https://github.com/google/cameratrapai",
        "runtime":"external_not_installed",
        "note":"Requires regional calibration, expert taxonomic review and licensing checks."
    },
    "nasa_firms_viirs": {
        "task":"satellite active fire observation",
        "provider":"NASA FIRMS",
        "model_reference":"https://firms.modaps.eosdis.nasa.gov/web-services/",
        "runtime":"external_credentials_required",
        "note":"Overpass detections are observations, not live wildfire perimeter measurements."
    }
}

@dataclass(frozen=True)
class Evidence:
    event_id: str
    source: str
    model_id: str
    confidence: float
    observed_at: datetime
    ingested_at: datetime
    synthetic: bool
    location_uncertainty_m: float | None = None
    verified_by_human: bool = False

def evidence_review(e: Evidence, *, max_age_minutes: float = 60) -> dict:
    if not e.event_id or not e.source or not e.model_id:
        raise ValueError("Missing provenance metadata")
    if e.observed_at.tzinfo is None or e.ingested_at.tzinfo is None:
        raise ValueError("Timestamps must be timezone-aware")
    if not (isfinite(e.confidence) and 0 <= e.confidence <= 1):
        raise ValueError("Confidence outside [0,1]")
    if not (isfinite(max_age_minutes) and max_age_minutes > 0):
        raise ValueError("Invalid staleness threshold")
    if e.location_uncertainty_m is not None and (
        not isfinite(e.location_uncertainty_m) or e.location_uncertainty_m < 0
    ):
        raise ValueError("Invalid spatial uncertainty")
    age_minutes=(e.ingested_at-e.observed_at).total_seconds()/60
    warnings=[]
    if age_minutes < 0: warnings.append("observation_timestamp_after_ingestion")
    if age_minutes > max_age_minutes: warnings.append("stale_observation")
    if e.synthetic: warnings.append("synthetic_evidence")
    if e.model_id not in MODEL_REGISTRY: warnings.append("unregistered_model")
    if e.location_uncertainty_m is None: warnings.append("missing_location_uncertainty")
    return {
        "event_id": e.event_id,
        "model_id": e.model_id,
        "provenance": {"source":e.source,"observed_at":e.observed_at.isoformat(),
                       "ingested_at":e.ingested_at.isoformat(),"synthetic":e.synthetic},
        "age_minutes":round(age_minutes,2),
        "warnings":warnings,
        "eligible_for_human_review":not warnings,
        "confirmed":bool(e.verified_by_human and not warnings),
        "automatic_enforcement":False,"dispatch_authorized":False,
    }

def binary_metrics(y_true: Iterable[int], scores: Iterable[float], threshold: float = .5) -> dict:
    """Holdout evaluation; report both classification and probabilistic error."""
    ys=list(y_true); ps=list(scores)
    if len(ys)!=len(ps) or not ys: raise ValueError("Nonempty equal-length inputs required")
    if not 0 <= threshold <= 1: raise ValueError("Invalid threshold")
    if any(y not in (0,1) for y in ys): raise ValueError("Labels must be binary")
    if any(not isfinite(p) or p<0 or p>1 for p in ps): raise ValueError("Invalid probability")
    tp=sum(y==1 and p>=threshold for y,p in zip(ys,ps))
    fp=sum(y==0 and p>=threshold for y,p in zip(ys,ps))
    fn=sum(y==1 and p<threshold for y,p in zip(ys,ps))
    tn=len(ys)-tp-fp-fn
    precision=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    f1=(2*precision*recall/(precision+recall)
        if precision is not None and recall is not None and precision+recall else None)
    brier=sum((p-y)**2 for y,p in zip(ys,ps))/len(ys)
    return {"n":len(ys),"tp":tp,"fp":fp,"fn":fn,"tn":tn,
            "precision":precision,"recall":recall,"f1":f1,"brier_score":brier,
            "threshold":threshold,"scope":"offline_holdout_only"}

def group_evaluation(rows: Iterable[tuple[str,int,float]], threshold: float=.5,
                     minimum_group_size:int=5)->dict:
    if minimum_group_size<1: raise ValueError("minimum_group_size must be positive")
    grouped={}
    for group,label,score in rows:
        if not group: raise ValueError("Missing evaluation group")
        grouped.setdefault(group,[]).append((label,score))
    return {
        group:({**binary_metrics([y for y,_ in records],[p for _,p in records],threshold),
                "group_size_warning":len(records)<minimum_group_size}
               ) for group,records in sorted(grouped.items())
    }
