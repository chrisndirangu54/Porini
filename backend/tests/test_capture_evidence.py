import wave
import pytest
from app.sensor_capture import read_wav, capture_rtsp_frame

def test_rtsp_scheme_guard():
    with pytest.raises(ValueError):
        capture_rtsp_frame("https://example.com/camera")

def test_wav_adapter(tmp_path):
    path=tmp_path/"sample.wav"
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(bytes(200))
    assert read_wav(str(path))["sample_count"]==100

def test_aes_gcm_roundtrip(tmp_path):
    pytest.importorskip("cryptography")
    from app.secure_evidence_store import save_encrypted, load_encrypted
    key=b"a"*32
    record=save_encrypted(str(tmp_path),"evidence".encode(),key)
    assert load_encrypted(str(tmp_path),record["object_id"],key)==b"evidence"
    assert b"evidence" not in (tmp_path/(record["object_id"]+".bin")).read_bytes()

def test_reject_bad_key(tmp_path):
    pytest.importorskip("cryptography")
    from app.secure_evidence_store import save_encrypted
    with pytest.raises(ValueError):
        save_encrypted(str(tmp_path),b"content",b"short")
