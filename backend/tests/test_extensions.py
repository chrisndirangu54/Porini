from datetime import datetime,timezone
from app.audio import extract_features, impulsive_candidate
from app.imagery import STACObservation, validate_scene
from app.connectors import ingest_mqtt_message

def test_audio_candidate_is_not_a_gunshot_claim():
    f=extract_features([0.0]*999+[0.95],1000)
    verdict=impulsive_candidate(f)
    assert verdict["candidate"]
    assert verdict["validated_classifier"] is False

def test_stac_requires_real_processing():
    scene=STACObservation(item_id="x",collection="sentinel-2-l2a",acquired_at=datetime.now(timezone.utc),
                          asset_href="https://example.org/image.tif",bbox=(36,-2,38,0))
    verdict=validate_scene(scene)
    assert verdict["alert_generated"] is False

def test_mqtt_allowlist_rejects_unknown_topic():
    try: ingest_mqtt_message("outside",b"{}",{"known"})
    except ValueError: return
    raise AssertionError("Topic should have been rejected")
