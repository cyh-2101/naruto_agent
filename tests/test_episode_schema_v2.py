from __future__ import annotations

import time
from dataclasses import replace
from datetime import UTC, datetime
from typing import TypeVar
from uuid import uuid4

from naruto_agent.core.actions import (
    CancelCondition,
    DirectionIntent,
    HorizontalIntent,
    SkillIntent,
    VerticalIntent,
)
from naruto_agent.core.combat_state import (
    EntityOwner,
    EntityType,
    SceneEntity,
    TemporalCombatState,
)
from naruto_agent.core.contracts import Point2D
from naruto_agent.core.enums import CharacterId
from naruto_agent.core.estimates import Estimate
from naruto_agent.data.models import (
    EpisodeManifest,
    EpisodeRuntimeEvent,
    EpisodeStreamRole,
    FeatureAvailability,
    SemanticActionRecord,
)

RecordT = TypeVar("RecordT")


def _known(value: RecordT, timestamp_ns: int) -> Estimate[RecordT]:
    return Estimate.known(
        value,
        confidence=0.9,
        observed_at_ns=timestamp_ns,
        valid_until_ns=timestamp_ns + 1_000,
        source="synthetic_test",
        provenance="unit_test",
    )


def test_temporal_state_runtime_event_serialization_round_trip() -> None:
    now = time.monotonic_ns()
    state = TemporalCombatState.unavailable(now, source="not_implemented_test")
    event = EpisodeRuntimeEvent(
        schema_version=2,
        timestamp_ns=now,
        stream=EpisodeStreamRole.TEMPORAL_COMBAT_STATE,
        status=FeatureAvailability.VALID,
        payload=state.to_record(),
    )
    restored = EpisodeRuntimeEvent.model_validate_json(event.model_dump_json())
    assert restored == event
    assert restored.payload is not None
    self_health = restored.payload["self"]["health"]
    assert self_health["status"] == FeatureAvailability.NOT_IMPLEMENTED.value
    assert self_health["value"] is None


def test_scene_entity_contract_serializes_visible_evidence() -> None:
    now = time.monotonic_ns()
    entity = SceneEntity(
        track_id="synthetic-entity-1",
        entity_type=_known(EntityType.PROJECTILE, now),
        position=_known(Point2D(0.25, 0.5), now),
        velocity=_known(Point2D(0.01, 0.0), now),
        owner=_known(EntityOwner.SELF, now),
        first_observed_at_ns=now,
        last_observed_at_ns=now,
    )
    payload = replace(
        TemporalCombatState.unavailable(now, source="test"),
        scene_entities=(entity,),
    ).to_record()
    assert payload["scene_entities"][0]["entity_type"]["value"] == "projectile"
    assert payload["scene_entities"][0]["owner"]["value"] == "self"


def test_legacy_v1_manifest_remains_readable() -> None:
    now = time.monotonic_ns()
    payload = {
        "schema_version": 1,
        "episode_id": str(uuid4()),
        "session_id": str(uuid4()),
        "source_type": "scripted_agent",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "started_monotonic_ns": now,
        "controlled_character": CharacterId.TAKA_SASUKE.value,
        "lineup": [CharacterId.TAKA_SASUKE.value],
        "emulator_profile_id": "legacy-test",
        "capture_config_hash": "capture",
        "control_config_hash": "control",
        "character_config_hash": "character",
    }
    manifest = EpisodeManifest.model_validate(payload)
    assert manifest.schema_version == 1
    assert manifest.streams == []
    assert manifest.policy_version is None


def test_runtime_event_distinguishes_not_implemented_from_unknown() -> None:
    now = time.monotonic_ns()
    not_implemented = EpisodeRuntimeEvent(
        schema_version=2,
        timestamp_ns=now,
        stream=EpisodeStreamRole.OBSERVATION_VIEWS,
        status=FeatureAvailability.NOT_IMPLEMENTED,
        reason="view builder not connected to recorder",
    )
    unknown = EpisodeRuntimeEvent(
        schema_version=2,
        timestamp_ns=now,
        stream=EpisodeStreamRole.PERCEPTION_ESTIMATES,
        status=FeatureAvailability.UNKNOWN,
        reason="value was not visible",
    )
    assert not_implemented.status is not unknown.status
    assert not_implemented.payload is None and unknown.payload is None


def test_semantic_action_record_serialization_round_trip() -> None:
    now = time.monotonic_ns()
    action = SemanticActionRecord(
        schema_version=2,
        timestamp_ns=now,
        vertical=VerticalIntent.UP,
        horizontal=HorizontalIntent.RIGHT,
        skill=SkillIntent.NORMAL_ATTACK,
        direction=DirectionIntent.NEUTRAL,
        hold_ms=25,
        deadline_ns=now + 1_000_000,
        cancel_condition=CancelCondition.ON_LOW_CONFIDENCE,
        confidence=0.9,
    )
    assert SemanticActionRecord.model_validate_json(action.model_dump_json()) == action
