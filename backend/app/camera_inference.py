"""Optional real camera-trap inference; never fabricates detections."""
from pathlib import Path
from .multimodal import local_asset

def detect_with_speciesnet(image_path: str, evidence_root: str) -> dict:
    p=local_asset(image_path,evidence_root)
    if p.suffix.lower() not in {".jpg",".jpeg",".png"}: raise ValueError("Unsupported image file")
    try:
        from speciesnet import SpeciesNet
    except ImportError as e:
        raise RuntimeError("Install the pinned SpeciesNet package and licensed weights") from e
    # Current SpeciesNet API expects file_paths and location metadata as inputs.
    model=SpeciesNet()
    result=model.predict(file_paths=[str(p)])
    return {"status":"inference_completed","model":"speciesnet",
            "result":result,"human_review_required":True,
            "automatic_enforcement":False,"model_validation":"not_established"}
