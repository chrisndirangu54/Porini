"""Optional open-source acoustic feature extraction and conservative event candidate scoring.

This is NOT a validated gunshot classifier. Actual models require labeled field data,
calibration, sensor sync and held-out evaluation before triggering operations.
"""
from dataclasses import dataclass
from typing import Sequence
import math

@dataclass
class AudioFeatures:
    rms: float
    peak: float
    crest_factor: float
    clipping_fraction: float
    duration_s: float

def extract_features(samples: Sequence[float], sample_rate: int) -> AudioFeatures:
    if sample_rate <= 0 or not samples:
        raise ValueError("Provide non-empty normalized audio and positive sample rate")
    if len(samples)>sample_rate*120:
        raise ValueError("Maximum 120 seconds")
    peak=max(abs(v) for v in samples)
    rms=math.sqrt(sum(v*v for v in samples)/len(samples))
    return AudioFeatures(rms,peak,peak/max(rms,1e-12),
                         sum(abs(v)>=0.999 for v in samples)/len(samples),
                         len(samples)/sample_rate)

def impulsive_candidate(features: AudioFeatures) -> dict:
    suspicious=features.crest_factor>7 and features.peak>0.15
    return {"candidate":suspicious, "event_type":"impulsive_sound_unclassified",
            "confidence":None,"validated_classifier":False,
            "reason":"Crest-factor heuristic only; cannot distinguish gunshots, thunder or other transients."}
