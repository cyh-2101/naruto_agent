from __future__ import annotations

import time
from dataclasses import replace
from typing import TypeVar

import pytest

from naruto_agent.core.actions import (
    ActionCapabilities,
    DirectionIntent,
    HorizontalIntent,
    LegacyControlAdapter,
    SemanticAction,
    SkillIntent,
    VerticalIntent,
    compose_movement,
)
from naruto_agent.core.combat_state import CombatantState, TemporalCombatState
from naruto_agent.core.contracts import ControlCommand, PolicyOutput
from naruto_agent.core.enums import CharacterId, MovementDirection
from naruto_agent.core.estimates import Estimate, EstimateStatus, UnavailableReason
from naruto_agent.core.observations import ObservationViewBuilder, ObservationViewType
from naruto_agent.runtime.input.mock import MockInputBackend
from naruto_agent.runtime.safety import ActionScheduler, SafetySnapshot
from naruto_agent.runtime.semantic import SemanticActionDispatcher

KnownT = TypeVar("KnownT")


def _known(value: KnownT, timestamp_ns: int, *, confidence: float = 1.0) -> Estimate[KnownT]:
    return Estimate.known(
        value,
        confidence=confidence,
        observed_at_ns=timestamp_ns,
        valid_until_ns=timestamp_ns + 1_000_000,
        source="synthetic_test",
        provenance="unit_test",
        source_version="test-v1",
    )


def _state(timestamp_ns: int) -> TemporalCombatState:
    base = TemporalCombatState.unavailable(timestamp_ns, source="test_not_implemented")
    self_state = replace(
        CombatantState.unavailable(timestamp_ns, source="test"),
        identity=_known(CharacterId.TAKA_SASUKE, timestamp_ns),
        health=_known(0.0, timestamp_ns),
        substitution_ready=_known(False, timestamp_ns),
    )
    opponent_state = replace(
        CombatantState.unavailable(timestamp_ns, source="test"),
        identity=_known(CharacterId.WHITE_MASK, timestamp_ns),
        health=_known(0.75, timestamp_ns),
    )
    return replace(
        base, sequence_id="test-sequence", self_state=self_state, opponent_state=opponent_state
    )


def test_estimate_preserves_false_and_zero_as_known_values() -> None:
    now = time.monotonic_ns()
    zero = _known(0.0, now)
    false = _known(False, now)
    unknown = Estimate.unavailable(
        UnavailableReason.NOT_OBSERVED,
        observed_at_ns=now,
        valid_until_ns=now + 10,
        source="test",
        provenance="unit_test",
    )
    assert zero.value == 0.0 and zero.status_at(now) is EstimateStatus.VALID
    assert false.value is False and false.status_at(now) is EstimateStatus.VALID
    assert unknown.value is None and unknown.status_at(now) is EstimateStatus.UNKNOWN


def test_estimate_confidence_freshness_and_staleness() -> None:
    now = time.monotonic_ns()
    estimate = _known("active", now, confidence=0.79)
    assert estimate.is_fresh_at(now)
    assert not estimate.is_usable_at(now, min_confidence=0.8)
    assert estimate.status_at(now + 1_000_001) is EstimateStatus.STALE


def test_estimate_rejects_ambiguous_none_without_reason() -> None:
    now = time.monotonic_ns()
    with pytest.raises(ValueError, match="unavailable_reason"):
        Estimate(
            value=None,
            confidence=0.0,
            observed_at_ns=now,
            valid_until_ns=now,
            source="test",
            provenance="unit_test",
        )


def test_strategic_intent_is_optional_in_legacy_policy_output() -> None:
    output = PolicyOutput(
        timestamp_ns=time.monotonic_ns(),
        strategic=None,
        macro=None,
        control=None,
        confidence=0.0,
    )
    assert output.strategic is None


def test_observation_views_enforce_identity_boundaries_in_serialization() -> None:
    now = time.monotonic_ns()
    builder = ObservationViewBuilder(configured_self_id=CharacterId.TAKA_SASUKE)
    state = _state(now)

    ir = builder.build(state, ObservationViewType.IDENTITY_RICH)
    sq = builder.build(state, ObservationViewType.SELF_QUALIFIED)
    iq = builder.build(state, ObservationViewType.IDENTITY_QUIET)

    assert ir.self_features["character_id"] == CharacterId.TAKA_SASUKE.value
    assert ir.opponent_features["character_id"] == CharacterId.WHITE_MASK.value
    assert sq.self_features["character_id"] == CharacterId.TAKA_SASUKE.value
    assert "character_id" not in sq.opponent_features
    assert "character_id" not in iq.self_features
    assert "character_id" not in iq.opponent_features
    assert CharacterId.WHITE_MASK.value not in sq.to_json()
    assert CharacterId.TAKA_SASUKE.value not in iq.to_json()
    assert CharacterId.WHITE_MASK.value not in iq.to_json()


def test_ir_omits_low_confidence_identity() -> None:
    now = time.monotonic_ns()
    state = _state(now)
    opponent = replace(
        state.opponent_state,
        identity=_known(CharacterId.WHITE_MASK, now, confidence=0.79),
    )
    view = ObservationViewBuilder(
        configured_self_id=CharacterId.TAKA_SASUKE,
        identity_confidence_threshold=0.8,
    ).build(replace(state, opponent_state=opponent), ObservationViewType.IDENTITY_RICH)
    assert "character_id" not in view.opponent_features


@pytest.mark.parametrize(
    ("vertical", "horizontal", "expected"),
    [
        (VerticalIntent.NEUTRAL, HorizontalIntent.NEUTRAL, MovementDirection.NEUTRAL),
        (VerticalIntent.UP, HorizontalIntent.NEUTRAL, MovementDirection.UP),
        (VerticalIntent.DOWN, HorizontalIntent.NEUTRAL, MovementDirection.DOWN),
        (VerticalIntent.NEUTRAL, HorizontalIntent.LEFT, MovementDirection.LEFT),
        (VerticalIntent.NEUTRAL, HorizontalIntent.RIGHT, MovementDirection.RIGHT),
        (VerticalIntent.UP, HorizontalIntent.LEFT, MovementDirection.UP_LEFT),
        (VerticalIntent.UP, HorizontalIntent.RIGHT, MovementDirection.UP_RIGHT),
        (VerticalIntent.DOWN, HorizontalIntent.LEFT, MovementDirection.DOWN_LEFT),
        (VerticalIntent.DOWN, HorizontalIntent.RIGHT, MovementDirection.DOWN_RIGHT),
    ],
)
def test_factorized_movement_composition(
    vertical: VerticalIntent,
    horizontal: HorizontalIntent,
    expected: MovementDirection,
) -> None:
    assert compose_movement(vertical, horizontal) is expected


def _allow_basic(timestamp_ns: int) -> ActionCapabilities:
    return ActionCapabilities(
        evaluated_at_ns=timestamp_ns,
        valid_until_ns=timestamp_ns + 1_000_000,
        allowed_vertical=frozenset(VerticalIntent),
        allowed_horizontal=frozenset(HorizontalIntent),
        allowed_skills=frozenset({SkillIntent.NONE, SkillIntent.NORMAL_ATTACK}),
        allowed_directions=frozenset({DirectionIntent.NEUTRAL}),
        source="synthetic_test",
        capability_version="test-v1",
    )


def test_capabilities_reject_unavailable_character_action_with_reason() -> None:
    now = time.monotonic_ns()
    action = SemanticAction(timestamp_ns=now, skill=SkillIntent.SKILL_1)
    decision = _allow_basic(now).evaluate(action, at_ns=now)
    assert not decision.allowed
    assert not decision.mask["skill"]
    assert "skill_unavailable" in decision.reasons


def test_capabilities_reject_after_validity_expires() -> None:
    now = time.monotonic_ns()
    decision = _allow_basic(now).evaluate(
        SemanticAction(timestamp_ns=now),
        at_ns=now + 1_000_001,
    )
    assert not decision.allowed
    assert not decision.mask["fresh"]
    assert "fresh_unavailable" in decision.reasons


class CountingAdapter(LegacyControlAdapter):
    def __init__(self) -> None:
        self.calls = 0

    def to_control_command(self, action: SemanticAction) -> ControlCommand:
        self.calls += 1
        return super().to_control_command(action)


class TestLiveBackend(MockInputBackend):
    __test__ = False

    @property
    def is_live(self) -> bool:
        return True


def _dry_run_snapshot() -> SafetySnapshot:
    return SafetySnapshot(
        dry_run=True,
        live_input_opt_in=False,
        window_focused=False,
        calibration_valid=False,
        capture_fresh=True,
        emergency_stop_active=False,
    )


def test_capability_rejection_stops_before_adapter_and_scheduler() -> None:
    now = time.monotonic_ns()
    backend = MockInputBackend()
    adapter = CountingAdapter()
    dispatcher = SemanticActionDispatcher(
        adapter=adapter,
        scheduler=ActionScheduler(backend),
    )
    result = dispatcher.dispatch(
        SemanticAction(timestamp_ns=now, skill=SkillIntent.SKILL_1),
        _allow_basic(now),
        _dry_run_snapshot(),
        at_ns=now,
    )
    assert not result.capability.allowed
    assert result.dispatch is None
    assert adapter.calls == 0
    assert backend.commands == []


def test_allowed_semantic_action_still_cannot_bypass_safety_gate() -> None:
    now = time.monotonic_ns()
    backend = TestLiveBackend()
    adapter = CountingAdapter()
    dispatcher = SemanticActionDispatcher(
        adapter=adapter,
        scheduler=ActionScheduler(backend),
    )
    result = dispatcher.dispatch(
        SemanticAction(timestamp_ns=now, skill=SkillIntent.NORMAL_ATTACK),
        _allow_basic(now),
        _dry_run_snapshot(),
        at_ns=now,
    )
    assert result.capability.allowed
    assert result.dispatch is not None
    assert result.dispatch.reason == "dry_run"
    assert not result.dispatch.executed
    assert backend.commands == []
    assert backend.release_count == 1
