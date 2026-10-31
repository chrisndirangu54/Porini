from datetime import datetime, timezone
import pytest
from backend.app.multimodal import InferenceRequest, local_asset, run_image
from backend.app.stac_pipeline import scene_metadata

def test_local_file_restriction(tmp_path):
    root=tmp_path/"evidence";root.mkdir()
    (root/"test.jpg").write_bytes(b"test")
    assert run_image(InferenceRequest(model="speciesnet",image_path="test.jpg"),str(root))["detections"]==[]
    with pytest.raises(ValueError):local_asset("../outside.txt",str(root))

def test_stac_no_false_alert():
    f={"id":"x","collection":"sentinel-2-l2a","bbox":[30,-2,31,-1],
       "properties":{"datetime":"2026-10-30T00:00:00Z"},"assets":{"visual":{}}}
    result=scene_metadata(f)
    assert not result["fire_confirmed"] and result["status"]=="metadata_only"
