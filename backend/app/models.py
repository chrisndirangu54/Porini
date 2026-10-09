from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator

class Modality(str, Enum):
    acoustic = "acoustic"
    camera = "camera"
    thermal = "thermal"
    drone = "drone"
    satellite = "satellite"
    collar = "collar"
    iot = "iot"
    ranger = "ranger"

class EventIn(BaseModel):
    source_id: str = Field(min_length=2, max_length=120)
    modality: Modality
    event_type: str = Field(min_length=3, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    confidence: float = Field(ge=0, le=1)
    severity: int = Field(ge=1, le=5)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uncertainty_m: float = Field(default=250, ge=0, le=100000)
    synthetic: bool = False
    evidence_uri: str | None = Field(default=None, max_length=2048)
    notes: str | None = Field(default=None, max_length=1000)
    external_id: str | None = Field(default=None, max_length=200)

    @field_validator("timestamp")
    @classmethod
    def ensure_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must include timezone")
        return value

class Event(EventIn):
    id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str | None = None

class Incident(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    latitude: float
    longitude: float
    priority: Literal["P1", "P2", "P3", "P4"]
    confidence: float
    severity: int
    uncertainty_m: float
    status: Literal["open", "acknowledged", "investigating", "resolved"] = "open"
    event_ids: list[str] = Field(default_factory=list)
    modalities: list[str] = Field(default_factory=list)
    synthetic: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusUpdate(BaseModel):
    status: Literal["acknowledged", "investigating", "resolved"]

class AssignmentIn(BaseModel):
    ranger_id: str = Field(min_length=2, max_length=120)
    notes: str = Field(default="", max_length=1000)

class DroneRequestIn(BaseModel):
    drone_id: str = Field(min_length=2, max_length=120)
    purpose: str = Field(min_length=5, max_length=300)

class ApprovalIn(BaseModel):
    approver_id: str = Field(min_length=2, max_length=120)
    approved: bool
    note: str = Field(default="", max_length=1000)
