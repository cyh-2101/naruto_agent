from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Generic, TypeAlias, TypeVar

from naruto_agent.core.enums import CharacterId
from naruto_agent.core.observations import ObservationViewType


class TrainingMethod(StrEnum):
    UNTRAINED = "untrained"
    SCRIPTED = "scripted"
    BEHAVIOR_CLONING = "behavior_cloning"
    OFFLINE_RL = "offline_rl"
    ONLINE_RL = "online_rl"
    DISTILLATION = "distillation"


class ArtifactStatus(StrEnum):
    DECLARED = "declared"
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    PROMOTED = "promoted"
    RETIRED = "retired"


class OpponentSource(StrEnum):
    SCRIPTED = "scripted"
    POLICY_SNAPSHOT = "policy_snapshot"
    HUMAN_DEMONSTRATION = "human_demonstration"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class PolicyMetadata:
    policy_id: str
    version: str
    status: ArtifactStatus
    training_method: TrainingMethod
    observation_view: ObservationViewType
    supported_characters: tuple[CharacterId, ...]
    model_version: str | None
    dataset_ids: tuple[str, ...]
    created_at_utc: datetime
    code_commit: str | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.policy_id.strip() or not self.version.strip():
            raise ValueError("policy id and version cannot be empty")


@dataclass(frozen=True, slots=True)
class OpponentMetadata:
    opponent_id: str
    version: str
    source: OpponentSource
    character_id: CharacterId | None
    policy_id: str | None
    created_at_utc: datetime
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.opponent_id.strip() or not self.version.strip():
            raise ValueError("opponent id and version cannot be empty")


@dataclass(frozen=True, slots=True)
class DatasetMetadata:
    dataset_id: str
    version: str
    schema_version: int
    immutable: bool
    source_episode_ids: tuple[str, ...]
    created_at_utc: datetime
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.dataset_id.strip() or not self.version.strip():
            raise ValueError("dataset id and version cannot be empty")
        if self.schema_version < 1:
            raise ValueError("schema_version must be positive")


MetadataT = TypeVar("MetadataT")


@dataclass(slots=True)
class MetadataRegistry(Generic[MetadataT]):
    """Typed in-memory catalog only; no league, sampling, or training behavior."""

    _items: dict[str, MetadataT] = field(default_factory=dict)

    def register(self, key: str, item: MetadataT) -> None:
        if not key.strip():
            raise ValueError("registry key cannot be empty")
        if key in self._items:
            raise ValueError(f"registry key already exists: {key}")
        self._items[key] = item

    def get(self, key: str) -> MetadataT:
        try:
            return self._items[key]
        except KeyError as exc:
            raise KeyError(f"unknown registry key: {key}") from exc

    def values(self) -> Iterable[MetadataT]:
        return tuple(self._items.values())


PolicyRegistry: TypeAlias = MetadataRegistry[PolicyMetadata]
OpponentRegistry: TypeAlias = MetadataRegistry[OpponentMetadata]
DatasetRegistry: TypeAlias = MetadataRegistry[DatasetMetadata]
