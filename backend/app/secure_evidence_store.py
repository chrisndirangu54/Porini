"""Local encrypted evidence vault prototype. Not a replacement for managed KMS/object storage."""
import hashlib, os
from pathlib import Path
from uuid import uuid4

def save_encrypted(root: str, data: bytes, key: bytes):
    if not data or len(data) > 20_000_000:
        raise ValueError("Evidence length outside supported bounds")
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as exc:
        raise RuntimeError("Install cryptography for encrypted evidence") from exc
    if len(key) != 32:
        raise ValueError("AES-256 key must contain 32 random bytes")
    location = Path(root).resolve()
    location.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(location, 0o700)
    token = str(uuid4())
    nonce = os.urandom(12)
    digest = hashlib.sha256(data).hexdigest()
    blob = nonce + AESGCM(key).encrypt(nonce, data, token.encode())
    fd = os.open(str(location / (token + ".bin")), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(blob)
    return {"object_id": token, "sha256": digest, "bytes_size": len(data)}

def load_encrypted(root: str, object_id: str, key: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from uuid import UUID
    token = str(UUID(object_id))
    blob = (Path(root).resolve() / (token + ".bin")).read_bytes()
    return AESGCM(key).decrypt(blob[:12], blob[12:], token.encode())
