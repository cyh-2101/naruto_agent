from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from naruto_agent.core.contracts import ControlCommand
from naruto_agent.core.enums import ButtonAction, MovementDirection


class VerticalIntent(StrEnum):
    NEUTRAL = "neutral"
    UP = "up"
    DOWN = "down"


class HorizontalIntent(StrEnum):
    NEUTRAL = "neutral"
    LEFT = "left"
    RIGHT = "right"


class SkillIntent(StrEnum):
    NONE = "none"
    NORMAL_ATTACK = "normal_attack"
    SKILL_1 = "skill_1"
    SKILL_2 = "skill_2"
    ULTIMATE = "ultimate"
    SUBSTITUTION = "substitution"
    SECRET_SCROLL = "secret_scroll"
    SUMMON = "summon"
    SUBSKILL_1 = "subskill_1"
    SUBSKILL_2 = "subskill_2"


class DirectionIntent(StrEnum):
    NEUTRAL = "neutral"
    DIRECTION_1 = "direction_1"
    DIRECTION_2 = "direction_2"
    DIRECTION_3 = "direction_3"
    DIRECTION_4 = "direction_4"
    DIRECTION_5 = "direction_5"
    DIRECTION_6 = "direction_6"
    DIRECTION_7 = "direction_7"
    DIRECTION_8 = "direction_8"


class CancelCondition(StrEnum):
    NONE = "none"
    ON_HIT = "on_hit"
    ON_BLOCK = "on_block"
    ON_THREAT = "on_threat"
    ON_LOW_CONFIDENCE = "on_low_confidence"
    ON_FOCUS_LOSS = "on_focus_loss"


_MOVEMENT_COMPOSITION: dict[tuple[VerticalIntent, HorizontalIntent], MovementDirection] = {
    (VerticalIntent.NEUTRAL, HorizontalIntent.NEUTRAL): MovementDirection.NEUTRAL,
    (VerticalIntent.UP, HorizontalIntent.NEUTRAL): MovementDirection.UP,
    (VerticalIntent.DOWN, HorizontalIntent.NEUTRAL): MovementDirection.DOWN,
    (VerticalIntent.NEUTRAL, HorizontalIntent.LEFT): MovementDirection.LEFT,
    (VerticalIntent.NEUTRAL, HorizontalIntent.RIGHT): MovementDirection.RIGHT,
    (VerticalIntent.UP, HorizontalIntent.LEFT): MovementDirection.UP_LEFT,
    (VerticalIntent.UP, HorizontalIntent.RIGHT): MovementDirection.UP_RIGHT,
    (VerticalIntent.DOWN, HorizontalIntent.LEFT): MovementDirection.DOWN_LEFT,
    (VerticalIntent.DOWN, HorizontalIntent.RIGHT): MovementDirection.DOWN_RIGHT,
}


def compose_movement(vertical: VerticalIntent, horizontal: HorizontalIntent) -> MovementDirection:
    return _MOVEMENT_COMPOSITION[(vertical, horizontal)]


@dataclass(frozen=True, slots=True)
class SemanticAction:
    """Policy output expressed without any keyboard, coordinate, or emulator binding."""

    timestamp_ns: int
    vertical: VerticalIntent = VerticalIntent.NEUTRAL
    horizontal: HorizontalIntent = HorizontalIntent.NEUTRAL
    skill: SkillIntent = SkillIntent.NONE
    direction: DirectionIntent = DirectionIntent.NEUTRAL
    hold_ms: int = 0
    deadline_ns: int | None = None
    cancel_condition: CancelCondition = CancelCondition.NONE
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if self.timestamp_ns <= 0:
            raise ValueError("timestamp_ns must be positive")
        if self.hold_ms < 0:
            raise ValueError("hold_ms must be non-negative")
        if self.deadline_ns is not None and self.deadline_ns < self.timestamp_ns:
            raise ValueError("deadline_ns cannot precede timestamp_ns")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")

    @property
    def movement(self) -> MovementDirection:
        return compose_movement(self.vertical, self.horizontal)


@dataclass(frozen=True, slots=True)
class CapabilityDecision:
    allowed: bool
    mask: Mapping[str, bool]
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ActionCapabilities:
    """Calibrated legality/capability contract, intentionally separate from SafetyGate."""

    evaluated_at_ns: int
    valid_until_ns: int
    allowed_vertical: frozenset[VerticalIntent]
    allowed_horizontal: frozenset[HorizontalIntent]
    allowed_skills: frozenset[SkillIntent]
    allowed_directions: frozenset[DirectionIntent]
    source: str
    capability_version: str
    rejection_reasons: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.evaluated_at_ns <= 0 or self.valid_until_ns < self.evaluated_at_ns:
            raise ValueError("capability timestamps are invalid")
        if not self.source.strip() or not self.capability_version.strip():
            raise ValueError("capability source and version cannot be empty")

    @classmethod
    def unverified(cls, timestamp_ns: int, *, source: str = "unverified") -> ActionCapabilities:
        return cls(
            evaluated_at_ns=timestamp_ns,
            valid_until_ns=timestamp_ns,
            allowed_vertical=frozenset({VerticalIntent.NEUTRAL}),
            allowed_horizontal=frozenset({HorizontalIntent.NEUTRAL}),
            allowed_skills=frozenset({SkillIntent.NONE}),
            allowed_directions=frozenset({DirectionIntent.NEUTRAL}),
            source=source,
            capability_version="unverified",
            rejection_reasons={"default": "character mechanics are not calibrated"},
        )

    def evaluate(self, action: SemanticAction, *, at_ns: int) -> CapabilityDecision:
        checks = {
            "vertical": action.vertical in self.allowed_vertical,
            "horizontal": action.horizontal in self.allowed_horizontal,
            "skill": action.skill in self.allowed_skills,
            "direction": action.direction in self.allowed_directions,
            "fresh": self.evaluated_at_ns <= at_ns <= self.valid_until_ns,
            "deadline": action.deadline_ns is None or at_ns <= action.deadline_ns,
        }
        reasons: list[str] = []
        for factor, allowed in checks.items():
            if not allowed:
                reasons.append(self.rejection_reasons.get(factor, f"{factor}_unavailable"))
        return CapabilityDecision(allowed=all(checks.values()), mask=checks, reasons=tuple(reasons))


class LegacyControlAdapter:
    """Transitional semantic-to-ControlCommand adapter; it contains no key bindings."""

    _BUTTONS: Mapping[SkillIntent, ButtonAction] = {
        SkillIntent.NONE: ButtonAction.NONE,
        SkillIntent.NORMAL_ATTACK: ButtonAction.NORMAL_ATTACK,
        SkillIntent.SKILL_1: ButtonAction.SKILL_1,
        SkillIntent.SKILL_2: ButtonAction.SKILL_2,
        SkillIntent.ULTIMATE: ButtonAction.ULTIMATE,
        SkillIntent.SUBSTITUTION: ButtonAction.SUBSTITUTION,
        SkillIntent.SECRET_SCROLL: ButtonAction.SECRET_SCROLL,
        SkillIntent.SUMMON: ButtonAction.SUMMON,
    }

    def to_control_command(self, action: SemanticAction) -> ControlCommand:
        try:
            button = self._BUTTONS[action.skill]
        except KeyError as exc:
            raise ValueError(f"no verified legacy mapping for {action.skill.value}") from exc
        return ControlCommand(
            timestamp_ns=action.timestamp_ns,
            movement=action.movement,
            button=button,
            hold_ms=action.hold_ms,
            source="semantic_action_v2",
        )
