from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol, runtime_checkable

from naruto_agent.core.contracts import (
    BeliefState,
    ControlCommand,
    FramePacket,
    PerceptionState,
    PolicyOutput,
)


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
    def act(self, perception: PerceptionState, belief: BeliefState) -> PolicyOutput: ...
