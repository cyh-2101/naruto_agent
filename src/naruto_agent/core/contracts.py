from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from naruto_agent.core.enums import (
    AnimationState,
    ButtonAction,
    CharacterId,
    MovementDirection,
    RoundPhase,
    StrategicIntent,
)

ImageArray = NDArray[np.uint8]


@dataclass(frozen=True, slots=True)
class Point2D:
    """Normalized image coordinate. Unknown coordinates are represented by None upstream."""

    x: float
    y: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.x <= 1.0 or not 0.0 <= self.y <= 1.0:
            raise ValueError("Point2D coordinates must be normalized to [0, 1]")


@dataclass(frozen=True, slots=True)
class FramePacket:
    frame_id: int
    timestamp_ns: int
    source_id: str
    image: ImageArray
    duplicate: bool = False
    dropped_before: int = 0

    def __post_init__(self) -> None:
        if self.frame_id < 0:
            raise ValueError("frame_id must be non-negative")
        if self.timestamp_ns <= 0:
            raise ValueError("timestamp_ns must be positive")
        if self.image.ndim != 3 or self.image.shape[2] not in (3, 4):
            raise ValueError("image must have shape HxWx3 or HxWx4")
        if self.image.dtype != np.uint8:
            raise ValueError("image dtype must be uint8")
        if self.dropped_before < 0:
            raise ValueError("dropped_before must be non-negative")


@dataclass(frozen=True, slots=True)
class PerceptionState:
    timestamp_ns: int
    active_character: CharacterId = CharacterId.UNKNOWN
    self_position: Point2D | None = None
    opponent_position: Point2D | None = None
    self_health: float | None = None
    opponent_health: float | None = None
    self_animation: AnimationState = AnimationState.UNKNOWN
    opponent_animation: AnimationState = AnimationState.UNKNOWN
    round_phase: RoundPhase = RoundPhase.UNKNOWN
    confidence: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.timestamp_ns <= 0:
            raise ValueError("timestamp_ns must be positive")
        for name, value in (
            ("self_health", self.self_health),
            ("opponent_health", self.opponent_health),
        ):
            if value is not None and not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")
        for key, value in self.confidence.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"confidence[{key!r}] must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class BeliefState:
    timestamp_ns: int
    opponent_substitution_ready_probability: float | None = None
    opponent_skill_ready_probability: Mapping[str, float] = field(default_factory=dict)
    aggression_score: float | None = None
    risk_score: float | None = None
    uncertainty: float = 1.0

    def __post_init__(self) -> None:
        if self.timestamp_ns <= 0:
            raise ValueError("timestamp_ns must be positive")
        probabilities = [
            self.opponent_substitution_ready_probability,
            *self.opponent_skill_ready_probability.values(),
        ]
        for value in probabilities:
            if value is not None and not 0.0 <= value <= 1.0:
                raise ValueError("belief probabilities must be in [0, 1]")
        if not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError("uncertainty must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class StrategicDecision:
    timestamp_ns: int
    intent: StrategicIntent
    confidence: float
    reason_code: str | None = None

    def __post_init__(self) -> None:
        if self.timestamp_ns <= 0:
            raise ValueError("timestamp_ns must be positive")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class MacroActionRequest:
    timestamp_ns: int
    character_id: CharacterId
    name: str
    parameters: Mapping[str, float | int | str | bool] = field(default_factory=dict)
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if self.timestamp_ns <= 0:
            raise ValueError("timestamp_ns must be positive")
        if not self.name.strip():
            raise ValueError("macro action name cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class ControlCommand:
    timestamp_ns: int
    movement: MovementDirection = MovementDirection.NEUTRAL
    button: ButtonAction = ButtonAction.NONE
    hold_ms: int = 0
    source: str = "unknown"

    def __post_init__(self) -> None:
        if self.timestamp_ns <= 0:
            raise ValueError("timestamp_ns must be positive")
        if self.hold_ms < 0:
            raise ValueError("hold_ms must be non-negative")


@dataclass(frozen=True, slots=True)
class PolicyOutput:
    timestamp_ns: int
    strategic: StrategicDecision | None
    macro: MacroActionRequest | None
    control: ControlCommand | None
    confidence: float

    def __post_init__(self) -> None:
        if self.timestamp_ns <= 0:
            raise ValueError("timestamp_ns must be positive")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
