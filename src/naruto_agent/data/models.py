from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from naruto_agent.core.actions import (
    CancelCondition,
    DirectionIntent,
    HorizontalIntent,
    SkillIntent,
    VerticalIntent,
)
from naruto_agent.core.enums import ButtonAction, CharacterId, MovementDirection
from naruto_agent.core.observations import ObservationViewType


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


class FeatureAvailability(StrEnum):
    ABSENT = "absent"
    NOT_IMPLEMENTED = "not_implemented"
    UNKNOWN = "unknown"
    INVALID = "invalid"
    STALE = "stale"
    VALID = "valid"


class EpisodeStreamRole(StrEnum):
    RAW_FRAMES = "raw_frames"
    FRAME_INDEX = "frame_index"
    INPUT_EVENTS = "input_events"
    CONTROL_INTERVALS = "control_intervals"
    PERCEPTION_ESTIMATES = "perception_estimates"
    TEMPORAL_COMBAT_STATE = "temporal_combat_state"
    OBSERVATION_VIEWS = "observation_views"
    SEMANTIC_ACTIONS = "semantic_actions"
    ACTION_CAPABILITIES = "action_capabilities"
    ACTION_MASKS = "action_masks"
    SCHEDULER_DECISIONS = "scheduler_decisions"
    SAFETY_DECISIONS = "safety_decisions"
    ANNOTATIONS = "annotations"


class EpisodeStreamDescriptor(StrictModel):
    role: EpisodeStreamRole
    schema_version: int = Field(ge=1)
    status: FeatureAvailability
    relative_path: str | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def validate_path_and_reason(self) -> EpisodeStreamDescriptor:
        if self.status is FeatureAvailability.VALID and not self.relative_path:
            raise ValueError("valid episode streams require relative_path")
        if self.status is FeatureAvailability.NOT_IMPLEMENTED and not self.reason:
            raise ValueError("not-implemented episode streams require reason")
        return self


class EpisodeFile(StrictModel):
    role: str
    relative_path: str
    sha256: str | None = None


class FrameIndexEvent(StrictModel):
    schema_version: Literal[1, 2]
    frame_id: int = Field(ge=0)
    timestamp_ns: int = Field(gt=0)
    video_pts: int | None = Field(default=None, ge=0)
    duplicate: bool = False
    dropped_before: int = Field(default=0, ge=0)


class ControlStateInterval(StrictModel):
    schema_version: Literal[1, 2]
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
    schema_version: Literal[1, 2]
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
    policy_version: str | None = None
    calibration_profile_version: str | None = None
    character_config_version: str | None = None
    observation_view_version: str | None = None
    streams: list[EpisodeStreamDescriptor] = Field(default_factory=list)
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
    schema_version: Literal[1, 2]
    timestamp_ns: int = Field(gt=0)
    device: str
    key: str
    event_type: Literal["down", "up"]
    source: Literal["human", "agent", "system"]


class ActionEvent(StrictModel):
    schema_version: Literal[1, 2]
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


class EstimateRecord(StrictModel):
    value: Any | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    observed_at_ns: int = Field(gt=0)
    valid_until_ns: int = Field(gt=0)
    source: str
    provenance: str
    source_version: str | None = None
    unavailable_reason: str | None = None
    status: FeatureAvailability

    @model_validator(mode="after")
    def validate_estimate(self) -> EstimateRecord:
        if self.valid_until_ns < self.observed_at_ns:
            raise ValueError("estimate validity precedes observation")
        if self.status is FeatureAvailability.VALID and self.value is None:
            raise ValueError("valid estimate requires a value")
        return self


class EpisodeRuntimeEvent(StrictModel):
    """Versioned envelope for optional V2 streams without inventing missing payloads."""

    schema_version: Literal[2]
    timestamp_ns: int = Field(gt=0)
    stream: EpisodeStreamRole
    status: FeatureAvailability
    payload: dict[str, Any] | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> EpisodeRuntimeEvent:
        if self.status is FeatureAvailability.VALID and self.payload is None:
            raise ValueError("valid runtime event requires payload")
        if self.status is FeatureAvailability.NOT_IMPLEMENTED and not self.reason:
            raise ValueError("not-implemented runtime event requires reason")
        return self


class ObservationViewRecord(StrictModel):
    schema_version: Literal[1]
    timestamp_ns: int = Field(gt=0)
    view_type: ObservationViewType
    view_version: str
    payload: dict[str, Any]


class SemanticActionRecord(StrictModel):
    schema_version: Literal[2]
    timestamp_ns: int = Field(gt=0)
    vertical: VerticalIntent
    horizontal: HorizontalIntent
    skill: SkillIntent
    direction: DirectionIntent
    hold_ms: int = Field(ge=0)
    deadline_ns: int | None = Field(default=None, gt=0)
    cancel_condition: CancelCondition
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_deadline(self) -> SemanticActionRecord:
        if self.deadline_ns is not None and self.deadline_ns < self.timestamp_ns:
            raise ValueError("semantic action deadline precedes decision")
        return self


class ActionCapabilitiesRecord(StrictModel):
    schema_version: Literal[1]
    evaluated_at_ns: int = Field(gt=0)
    valid_until_ns: int = Field(gt=0)
    allowed_vertical: list[VerticalIntent]
    allowed_horizontal: list[HorizontalIntent]
    allowed_skills: list[SkillIntent]
    allowed_directions: list[DirectionIntent]
    source: str
    capability_version: str
    rejection_reasons: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_validity(self) -> ActionCapabilitiesRecord:
        if self.valid_until_ns < self.evaluated_at_ns:
            raise ValueError("capabilities expire before evaluation")
        return self


class ActionMaskRecord(StrictModel):
    schema_version: Literal[1]
    timestamp_ns: int = Field(gt=0)
    allowed: bool
    factor_mask: dict[str, bool]
    reasons: list[str] = Field(default_factory=list)


class DispatchDecisionRecord(StrictModel):
    schema_version: Literal[1]
    timestamp_ns: int = Field(gt=0)
    stage: Literal["scheduler", "safety_gate"]
    executed: bool
    simulated: bool
    reason: str
