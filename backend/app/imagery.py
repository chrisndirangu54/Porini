"""Metadata-first geospatial adapters; no invented satellite change detections."""
from datetime import datetime
from pydantic import BaseModel, Field

class STACObservation(BaseModel):
    item_id: str
    collection: str
    acquired_at: datetime
    asset_href: str
    cloud_cover_percent: float | None=Field(None,ge=0,le=100)
    gsd_meters: float | None=Field(None,gt=0)
    bbox: tuple[float,float,float,float]
    license: str | None=None

def validate_scene(scene: STACObservation) -> dict:
    xmin,ymin,xmax,ymax=scene.bbox
    if not (-180<=xmin<xmax<=180 and -90<=ymin<ymax<=90):
        raise ValueError("Invalid geographic bbox")
    if scene.acquired_at.tzinfo is None:
        raise ValueError("Acquisition time must include timezone")
    return {"item_id":scene.item_id,"usable_for_visual_review": scene.cloud_cover_percent is None or scene.cloud_cover_percent<60,
            "status":"metadata_only","alert_generated":False,
            "note":"Actual change detection requires raster reading, cloud masking, baseline alignment and validation."}
