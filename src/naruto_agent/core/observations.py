from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from naruto_agent.core.combat_state import CombatantState, SceneEntity, TemporalCombatState
from naruto_agent.core.contracts import Point2D
from naruto_agent.core.enums import CharacterId
from naruto_agent.core.estimates import Estimate


class ObservationViewType(StrEnum):
    IDENTITY_RICH = "ir"
    SELF_QUALIFIED = "sq"
    IDENTITY_QUIET = "iq"


@dataclass(frozen=True, slots=True)
class ObservationView:
    """Versioned policy projection. Hidden identity keys are absent, never null placeholders."""

    view_type: ObservationViewType
    view_version: str
    timestamp_ns: int
    self_features: dict[str, Any]
    opponent_features: dict[str, Any]
    relative_features: dict[str, Any]
    scene_entities: tuple[dict[str, Any], ...]
    schema_version: int = 1

    def to_policy_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "view_type": self.view_type.value,
            "view_version": self.view_version,
            "timestamp_ns": self.timestamp_ns,
            "self": self.self_features,
            "opponent": self.opponent_features,
            "relative": self.relative_features,
            "scene_entities": list(self.scene_entities),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_policy_dict(), sort_keys=True, separators=(",", ":"))


class ObservationViewBuilder:
    """Build IR/SQ/IQ views from one state without duplicating perception."""

    def __init__(
        self,
        *,
        configured_self_id: CharacterId,
        identity_confidence_threshold: float = 0.8,
        view_version: str = "1.0",
    ) -> None:
        if configured_self_id is CharacterId.UNKNOWN:
            raise ValueError("configured_self_id must be known")
        if not 0.0 <= identity_confidence_threshold <= 1.0:
            raise ValueError("identity_confidence_threshold must be in [0, 1]")
        if not view_version.strip():
            raise ValueError("view_version cannot be empty")
        self._configured_self_id = configured_self_id
        self._identity_threshold = identity_confidence_threshold
        self._view_version = view_version

    def build(self, state: TemporalCombatState, view_type: ObservationViewType) -> ObservationView:
        self_features = self._combatant_features(state.self_state, at_ns=state.timestamp_ns)
        opponent_features = self._combatant_features(state.opponent_state, at_ns=state.timestamp_ns)
        if view_type is ObservationViewType.IDENTITY_RICH:
            self._add_estimated_identity(
                self_features, state.self_state.identity, at_ns=state.timestamp_ns
            )
            self._add_estimated_identity(
                opponent_features, state.opponent_state.identity, at_ns=state.timestamp_ns
            )
        elif view_type is ObservationViewType.SELF_QUALIFIED:
            self_features["character_id"] = self._configured_self_id.value
        elif view_type is not ObservationViewType.IDENTITY_QUIET:
            raise ValueError(f"unsupported observation view: {view_type}")

        relative = {
            "delta": _policy_estimate(state.relative.delta, at_ns=state.timestamp_ns),
            "distance": _policy_estimate(state.relative.distance, at_ns=state.timestamp_ns),
            "distance_bucket": _policy_estimate(
                state.relative.distance_bucket, at_ns=state.timestamp_ns
            ),
            "screen_edge_relation": _policy_estimate(
                state.relative.screen_edge_relation, at_ns=state.timestamp_ns
            ),
            "round_phase": _policy_estimate(state.round_state.phase, at_ns=state.timestamp_ns),
            "round_timer_seconds": _policy_estimate(
                state.round_state.timer_seconds, at_ns=state.timestamp_ns
            ),
        }
        return ObservationView(
            view_type=view_type,
            view_version=self._view_version,
            timestamp_ns=state.timestamp_ns,
            self_features=self_features,
            opponent_features=opponent_features,
            relative_features=relative,
            scene_entities=tuple(
                self._scene_entity(entity, at_ns=state.timestamp_ns)
                for entity in state.scene_entities
            ),
        )

    def _add_estimated_identity(
        self,
        features: dict[str, Any],
        identity: Estimate[CharacterId],
        *,
        at_ns: int,
    ) -> None:
        if identity.is_usable_at(at_ns, min_confidence=self._identity_threshold):
            assert identity.value is not None
            if identity.value is not CharacterId.UNKNOWN:
                features["character_id"] = identity.value.value

    @staticmethod
    def _combatant_features(combatant: CombatantState, *, at_ns: int) -> dict[str, Any]:
        return {
            "health": _policy_estimate(combatant.health, at_ns=at_ns),
            "energy": _policy_estimate(combatant.energy, at_ns=at_ns),
            "position": _policy_estimate(combatant.position, at_ns=at_ns),
            "velocity": _policy_estimate(combatant.velocity, at_ns=at_ns),
            "action_phase": _policy_estimate(combatant.action_phase, at_ns=at_ns),
            "substitution_ready": _policy_estimate(combatant.substitution_ready, at_ns=at_ns),
            "skill_readiness": {
                name: _policy_estimate(estimate, at_ns=at_ns)
                for name, estimate in combatant.skill_readiness.items()
            },
        }

    @staticmethod
    def _scene_entity(entity: SceneEntity, *, at_ns: int) -> dict[str, Any]:
        return {
            "track_id": entity.track_id,
            "entity_type": _policy_estimate(entity.entity_type, at_ns=at_ns),
            "position": _policy_estimate(entity.position, at_ns=at_ns),
            "velocity": _policy_estimate(entity.velocity, at_ns=at_ns),
            "owner": _policy_estimate(entity.owner, at_ns=at_ns),
            "age_ns": max(0, at_ns - entity.first_observed_at_ns),
        }


def _policy_estimate(estimate: Estimate[Any], *, at_ns: int) -> dict[str, Any]:
    value = estimate.value
    if isinstance(value, StrEnum):
        value = value.value
    elif isinstance(value, Point2D):
        value = {"x": value.x, "y": value.y}
    return {
        "value": value,
        "confidence": estimate.confidence,
        "status": estimate.status_at(at_ns).value,
        "age_ns": max(0, at_ns - estimate.observed_at_ns),
    }
