"""Content-addressed on-disk evidence integrity metadata; no public media URLs."""
import hashlib
from pathlib import Path

def fingerprint_file(path: Path, *, max_size: int = 40_000_000) -> dict:
    if not path.is_file(): raise ValueError("Evidence not a regular file")
    size=path.stat().st_size
    if size > max_size: raise ValueError("Evidence too large")
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return {"sha256":h.hexdigest(),"size_bytes":size,"encryption_verified":False,
            "immutable_storage_verified":False}
