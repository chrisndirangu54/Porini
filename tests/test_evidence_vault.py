from backend.app.evidence_vault import fingerprint_file

def test_digest(tmp_path):
    p=tmp_path/"x.bin";p.write_bytes(b"porini")
    result=fingerprint_file(p)
    assert len(result["sha256"])==64
    assert not result["encryption_verified"]
