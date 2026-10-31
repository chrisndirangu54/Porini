"""Optional device readers: local RTSP video and WAV audio, no automatic classification."""
from pathlib import Path
from urllib.parse import urlsplit
import os, wave

def capture_rtsp_frame(rtsp_url: str):
    """Read one optical/thermal RTSP frame. Requires installed OpenCV and a provisioned camera."""
    if urlsplit(rtsp_url).scheme != "rtsp":
        raise ValueError("RTSP URL required")
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("Install optional opencv-python-headless driver") from exc
    stream = cv2.VideoCapture(rtsp_url)
    try:
        if not stream.isOpened():
            raise ConnectionError("Camera unavailable")
        ok, frame = stream.read()
        if not ok or frame is None:
            raise ConnectionError("No frame received")
        return frame
    finally:
        stream.release()

def read_wav(path: str, max_bytes: int = 20_000_000):
    """Local consented WAV sample. No microphone capture or AI inference."""
    p = Path(path).resolve(strict=True)
    if p.stat().st_size > max_bytes:
        raise ValueError("Audio exceeds capture limit")
    with wave.open(str(p), "rb") as w:
        return {"channels": w.getnchannels(), "sample_rate": w.getframerate(),
                "sample_count": w.getnframes(), "pcm": w.readframes(w.getnframes())}
