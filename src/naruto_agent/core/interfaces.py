from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Protocol, runtime_checkable

from naruto_agent.core.actions import SemanticAction
from naruto_agent.core.combat_state import TemporalCombatState
from naruto_agent.core.contracts import (
    BeliefState,
    ControlCommand,
    FramePacket,
    PerceptionState,
    PolicyOutput,
)
from naruto_agent.core.enums import CharacterId
from naruto_agent.core.observations import ObservationView


@runtime_checkable
class CaptureBackend(Protocol):
    @property
    def source_id(self) -> str: ...

    def start(self) -> None: ...

    def frames(self) -> Iterator[FramePacket]: ...

    def stop(self) -> None: ...


@runtime_checkable
class InputBackend(Protocol):
    @property
    def is_live(self) -> bool: ...

    def execute(self, command: ControlCommand) -> None: ...

    def key_down(self, key: str) -> None: ...

    def key_up(self, key: str) -> None: ...

    def timed_press(self, key: str, duration_ms: int) -> None: ...

    def release_all(self) -> None: ...


@runtime_checkable
class PerceptionModule(Protocol):
    def infer(self, frame: FramePacket) -> PerceptionState: ...


@runtime_checkable
class BeliefUpdater(Protocol):
    def update(
        self,
        perception: PerceptionState,
        previous_belief: BeliefState | None,
        previous_command: ControlCommand | None,
    ) -> BeliefState: ...


@runtime_checkable
class Policy(Protocol):
    """Legacy Work Order 001 policy boundary retained for compatibility."""

    def act(self, perception: PerceptionState, belief: BeliefState) -> PolicyOutput: ...


@runtime_checkable
class CharacterActionAdapter(Protocol):
    """Maps semantic outputs to legacy control commands without exposing key bindings."""

    def to_control_command(self, action: SemanticAction) -> ControlCommand: ...


@runtime_checkable
class TemporalStateEstimator(Protocol):
    def update(self, frame: FramePacket) -> TemporalCombatState: ...


@runtime_checkable
class TemporalPolicy(Protocol):
    def act(self, observation: ObservationView) -> SemanticAction: ...


@runtime_checkable
class SharedTemporalBackbone(Protocol):
    def encode(self, observation: ObservationView) -> Mapping[str, tuple[float, ...]]: ...


@runtime_checkable
class CharacterConditioningAdapter(Protocol):
    def condition(
        self,
        shared_features: Mapping[str, tuple[float, ...]],
        character_id: CharacterId,
    ) -> Mapping[str, tuple[float, ...]]: ...


@runtime_checkable
class FactorizedActionHeads(Protocol):
    def predict(
        self,
        conditioned_features: Mapping[str, tuple[float, ...]],
        *,
        timestamp_ns: int,
    ) -> SemanticAction: ...
