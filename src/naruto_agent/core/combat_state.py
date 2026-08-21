from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from naruto_agent.core.contracts import Point2D
from naruto_agent.core.enums import CharacterId, RoundPhase
from naruto_agent.core.estimates import Estimate, UnavailableReason


class ActionPhase(StrEnum):
    IDLE = "idle"
    STARTUP = "startup"
    ACTIVE = "active"
    RECOVERY = "recovery"
    HITSTUN = "hitstun"
    KNOCKDOWN = "knockdown"
    MOVEMENT = "movement"


class DistanceBucket(StrEnum):
    CLOSE = "close"
    MEDIUM = "medium"
    FAR = "far"


class ScreenEdgeRelation(StrEnum):
    NONE = "none"
    SELF_NEAR_EDGE = "self_near_edge"
    OPPONENT_NEAR_EDGE = "opponent_near_edge"
    BOTH_NEAR_EDGE = "both_near_edge"


class EntityType(StrEnum):
    PROJECTILE = "projectile"
    SUMMON = "summon"
    TRAP = "trap"
    AREA_EFFECT = "area_effect"
    PICKUP = "pickup"
    OTHER = "other"


class EntityOwner(StrEnum):
    SELF = "self"
    OPPONENT = "opponent"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


def _unknown(timestamp_ns: int, source: str) -> Estimate[Any]:
    return Estimate.unavailable(
        UnavailableReason.NOT_IMPLEMENTED,
        observed_at_ns=timestamp_ns,
        valid_until_ns=timestamp_ns,
        source=source,
        provenance="contract_placeholder",
    )


@dataclass(frozen=True, slots=True)
class CombatantState:
    identity: Estimate[CharacterId]
    health: Estimate[float]
    energy: Estimate[float]
    position: Estimate[Point2D]
    velocity: Estimate[Point2D]
    action_phase: Estimate[str]
    substitution_ready: Estimate[bool]
    skill_readiness: Mapping[str, Estimate[bool]] = field(default_factory=dict)

    @classmethod
    def unavailable(cls, timestamp_ns: int, *, source: str) -> CombatantState:
        return cls(
            identity=_unknown(timestamp_ns, source),
            health=_unknown(timestamp_ns, source),
            energy=_unknown(timestamp_ns, source),
            position=_unknown(timestamp_ns, source),
            velocity=_unknown(timestamp_ns, source),
            action_phase=_unknown(timestamp_ns, source),
            substitution_ready=_unknown(timestamp_ns, source),
        )


@dataclass(frozen=True, slots=True)
class RelativeCombatState:
    delta: Estimate[Point2D]
    distance: Estimate[float]
    distance_bucket: Estimate[DistanceBucket]
    screen_edge_relation: Estimate[ScreenEdgeRelation]

    @classmethod
    def unavailable(cls, timestamp_ns: int, *, source: str) -> RelativeCombatState:
        return cls(
            delta=_unknown(timestamp_ns, source),
            distance=_unknown(timestamp_ns, source),
            distance_bucket=_unknown(timestamp_ns, source),
            screen_edge_relation=_unknown(timestamp_ns, source),
        )


@dataclass(frozen=True, slots=True)
class SceneEntity:
    track_id: str
    entity_type: Estimate[EntityType]
    position: Estimate[Point2D]
    velocity: Estimate[Point2D]
    owner: Estimate[EntityOwner]
    first_observed_at_ns: int
    last_observed_at_ns: int

    def __post_init__(self) -> None:
        if not self.track_id.strip():
            raise ValueError("track_id cannot be empty")
        if self.first_observed_at_ns <= 0 or self.last_observed_at_ns < self.first_observed_at_ns:
            raise ValueError("scene entity timestamps are invalid")


@dataclass(frozen=True, slots=True)
class RoundState:
    phase: Estimate[RoundPhase]
    timer_seconds: Estimate[float]
    outcome: Estimate[str]

    @classmethod
    def unavailable(cls, timestamp_ns: int, *, source: str) -> RoundState:
        return cls(
            phase=_unknown(timestamp_ns, source),
            timer_seconds=_unknown(timestamp_ns, source),
            outcome=_unknown(timestamp_ns, source),
        )


@dataclass(frozen=True, slots=True)
class TemporalQuality:
    frame_fresh: bool
    frame_duplicate: bool
    dropped_before: int
    aggregate_confidence: float

    def __post_init__(self) -> None:
        if self.dropped_before < 0:
            raise ValueError("dropped_before must be non-negative")
        if not 0.0 <= self.aggregate_confidence <= 1.0:
            raise ValueError("aggregate_confidence must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class TemporalCombatState:
    """Canonical screen-only state; every uncertain value carries its own evidence."""

    timestamp_ns: int
    sequence_start_ns: int
    sequence_id: str
    self_state: CombatantState
    opponent_state: CombatantState
    relative: RelativeCombatState
    round_state: RoundState
    quality: TemporalQuality
    scene_entities: tuple[SceneEntity, ...] = ()
    schema_version: int = 2

    def __post_init__(self) -> None:
        if self.timestamp_ns <= 0 or self.sequence_start_ns <= 0:
            raise ValueError("state timestamps must be positive")
        if self.sequence_start_ns > self.timestamp_ns:
            raise ValueError("sequence_start_ns cannot exceed timestamp_ns")
        if not self.sequence_id.strip():
            raise ValueError("sequence_id cannot be empty")
        if self.schema_version != 2:
            raise ValueError("TemporalCombatState currently requires schema_version=2")

    @classmethod
    def unavailable(cls, timestamp_ns: int, *, source: str) -> TemporalCombatState:
        return cls(
            timestamp_ns=timestamp_ns,
            sequence_start_ns=timestamp_ns,
            sequence_id="unavailable",
            self_state=CombatantState.unavailable(timestamp_ns, source=source),
            opponent_state=CombatantState.unavailable(timestamp_ns, source=source),
            relative=RelativeCombatState.unavailable(timestamp_ns, source=source),
            round_state=RoundState.unavailable(timestamp_ns, source=source),
            quality=TemporalQuality(
                frame_fresh=False,
                frame_duplicate=False,
                dropped_before=0,
                aggregate_confidence=0.0,
            ),
        )

    def to_record(self) -> dict[str, Any]:
        def estimates(combatant: CombatantState) -> dict[str, Any]:
            return {
                "identity": combatant.identity.to_record(at_ns=self.timestamp_ns),
                "health": combatant.health.to_record(at_ns=self.timestamp_ns),
                "energy": combatant.energy.to_record(at_ns=self.timestamp_ns),
                "position": combatant.position.to_record(at_ns=self.timestamp_ns),
                "velocity": combatant.velocity.to_record(at_ns=self.timestamp_ns),
                "action_phase": combatant.action_phase.to_record(at_ns=self.timestamp_ns),
                "substitution_ready": combatant.substitution_ready.to_record(
                    at_ns=self.timestamp_ns
                ),
                "skill_readiness": {
                    name: estimate.to_record(at_ns=self.timestamp_ns)
                    for name, estimate in combatant.skill_readiness.items()
                },
            }

        return {
            "schema_version": self.schema_version,
            "timestamp_ns": self.timestamp_ns,
            "sequence_start_ns": self.sequence_start_ns,
            "sequence_id": self.sequence_id,
            "self": estimates(self.self_state),
            "opponent": estimates(self.opponent_state),
            "relative": {
                "delta": self.relative.delta.to_record(at_ns=self.timestamp_ns),
                "distance": self.relative.distance.to_record(at_ns=self.timestamp_ns),
                "distance_bucket": self.relative.distance_bucket.to_record(at_ns=self.timestamp_ns),
                "screen_edge_relation": self.relative.screen_edge_relation.to_record(
                    at_ns=self.timestamp_ns
                ),
            },
            "round": {
                "phase": self.round_state.phase.to_record(at_ns=self.timestamp_ns),
                "timer_seconds": self.round_state.timer_seconds.to_record(at_ns=self.timestamp_ns),
                "outcome": self.round_state.outcome.to_record(at_ns=self.timestamp_ns),
            },
            "scene_entities": [
                {
                    "track_id": entity.track_id,
                    "entity_type": entity.entity_type.to_record(at_ns=self.timestamp_ns),
                    "position": entity.position.to_record(at_ns=self.timestamp_ns),
                    "velocity": entity.velocity.to_record(at_ns=self.timestamp_ns),
                    "owner": entity.owner.to_record(at_ns=self.timestamp_ns),
                    "first_observed_at_ns": entity.first_observed_at_ns,
                    "last_observed_at_ns": entity.last_observed_at_ns,
                }
                for entity in self.scene_entities
            ],
            "quality": {
                "frame_fresh": self.quality.frame_fresh,
                "frame_duplicate": self.quality.frame_duplicate,
                "dropped_before": self.quality.dropped_before,
                "aggregate_confidence": self.quality.aggregate_confidence,
            },
        }
