from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from naruto_agent.core.enums import ButtonAction, CharacterId, MovementDirection


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourceType(StrEnum):
    HUMAN_DEMONSTRATION = "human_demonstration"
    SCRIPTED_AGENT = "scripted_agent"
    LEARNED_AGENT = "learned_agent"
    IMPORTED_VIDEO = "imported_video"


class QualityFlag(StrEnum):
    DROPPED_FRAMES = "dropped_frames"
    TIMESTAMP_GAP = "timestamp_gap"
    INCOMPLETE_FINALIZATION = "incomplete_finalization"
    FOCUS_LOSS = "focus_loss"
    EMERGENCY_STOP = "emergency_stop"
    ABORTED = "aborted"
    RAW_FRAME_FALLBACK = "raw_frame_fallback"


class EpisodeFile(StrictModel):
    role: str
    relative_path: str
    sha256: str | None = None


class FrameIndexEvent(StrictModel):
    schema_version: Literal[1]
    frame_id: int = Field(ge=0)
    timestamp_ns: int = Field(gt=0)
    video_pts: int | None = Field(default=None, ge=0)
    duplicate: bool = False
    dropped_before: int = Field(default=0, ge=0)


class ControlStateInterval(StrictModel):
    schema_version: Literal[1]
    start_ns: int = Field(gt=0)
    end_ns: int = Field(gt=0)
    movement: MovementDirection
    button: ButtonAction
    character_id: CharacterId
    source: Literal["human", "scripted", "policy", "dry_run"]
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_order(self) -> ControlStateInterval:
        if self.end_ns < self.start_ns:
            raise ValueError("control interval end precedes start")
        return self


class EpisodeManifest(StrictModel):
    schema_version: Literal[1]
    episode_id: UUID
    session_id: UUID
    source_type: SourceType
    started_at_utc: datetime
    ended_at_utc: datetime | None = None
    started_monotonic_ns: int = Field(gt=0)
    ended_monotonic_ns: int | None = Field(default=None, gt=0)
    controlled_character: CharacterId
    lineup: list[CharacterId]
    emulator_profile_id: str
    capture_config_hash: str
    control_config_hash: str
    character_config_hash: str
    code_commit: str | None = None
    model_version: str | None = None
    files: list[EpisodeFile] = Field(default_factory=list)
    quality_flags: list[QualityFlag] = Field(default_factory=list)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_time_order(self) -> EpisodeManifest:
        if (
            self.ended_monotonic_ns is not None
            and self.ended_monotonic_ns < self.started_monotonic_ns
        ):
            raise ValueError("episode ended before it started")
        if self.ended_at_utc is not None and self.ended_at_utc < self.started_at_utc:
            raise ValueError("UTC end time precedes start time")
        return self


class InputEvent(StrictModel):
    schema_version: Literal[1]
    timestamp_ns: int = Field(gt=0)
    device: str
    key: str
    event_type: Literal["down", "up"]
    source: Literal["human", "agent", "system"]


class ActionEvent(StrictModel):
    schema_version: Literal[1]
    start_ns: int = Field(gt=0)
    end_ns: int = Field(gt=0)
    movement: MovementDirection
    button: ButtonAction
    character_id: CharacterId
    source: Literal["human", "scripted", "policy", "pseudo_label"]
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_order(self) -> ActionEvent:
        if self.end_ns < self.start_ns:
            raise ValueError("action end precedes start")
        return self
