"""Multimodal research adapters: real local file inference where dependencies/weights exist.

No inference is invented. All inference is opt-in, offline, and returns
unverified candidates. Model outputs cannot drive enforcement or flight.
"""
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field

class InferenceRequest(BaseModel):
    model: Literal["speciesnet","megadetector_v6"]
    image_path: str = Field(min_length=1,max_length=1024)

class AudioRequest(BaseModel):
    model: Literal["birdnet"]
    audio_path: str = Field(min_length=1,max_length=1024)
    latitude: float|None = Field(default=None,ge=-90,le=90)
    longitude: float|None = Field(default=None,ge=-180,le=180)

def local_asset(path: str, root: str)->Path:
    """Restrict inference to files already staged in the dedicated evidence directory."""
    base=Path(root).expanduser().resolve(strict=True)
    item=(base/path).resolve(strict=True)
    if not item.is_relative_to(base) or not item.is_file():
        raise ValueError("Evidence path outside approved data directory")
    if item.stat().st_size>40_000_000:
        raise ValueError("Evidence file exceeds configured size limit")
    return item

def inference_readiness(model:str)->dict:
    import importlib.util
    deps={"speciesnet":"speciesnet","megadetector_v6":"megadetector","birdnet":"birdnet"}
    if model not in deps:raise ValueError("Unknown model")
    available=importlib.util.find_spec(deps[model]) is not None
    return {"model":model,"dependency_present":available,
            "configured":False,"inference_completed":False,
            "note":"Model weights, licenses, regional validation and operator configuration must be verified."}

def run_image(request:InferenceRequest, root:str)->dict:
    """Validation gate. Real inference is intentionally not claimed until supported SDK is configured."""
    p=local_asset(request.image_path,root)
    if p.suffix.lower() not in (".jpg",".jpeg",".png"):
        raise ValueError("Unsupported image format")
    readiness=inference_readiness(request.model)
    return {**readiness,"evidence_file":p.name,"detections":[],
            "status":"MODEL_INTEGRATION_REQUIRED","human_review_required":True}

def run_audio(request:AudioRequest, root:str)->dict:
    p=local_asset(request.audio_path,root)
    if p.suffix.lower() not in (".wav",".flac"):
        raise ValueError("Unsupported audio format")
    return {**inference_readiness(request.model),"evidence_file":p.name,
            "detections":[],"status":"MODEL_INTEGRATION_REQUIRED",
            "human_review_required":True}
