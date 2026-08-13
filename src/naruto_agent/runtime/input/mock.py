from __future__ import annotations

from naruto_agent.core.contracts import ControlCommand


class MockInputBackend:
    """Records commands and never sends operating-system input."""

    def __init__(self) -> None:
        self.commands: list[ControlCommand] = []
        self.release_count = 0
        self.events: list[tuple[str, str]] = []
        self.held_keys: set[str] = set()

    @property
    def is_live(self) -> bool:
        return False

    def execute(self, command: ControlCommand) -> None:
        self.commands.append(command)

    def key_down(self, key: str) -> None:
        self.held_keys.add(key)
        self.events.append(("down", key))

    def key_up(self, key: str) -> None:
        self.held_keys.discard(key)
        self.events.append(("up", key))

    def timed_press(self, key: str, duration_ms: int) -> None:
        if duration_ms < 0:
            raise ValueError("duration_ms must be non-negative")
        self.key_down(key)
        self.key_up(key)

    def release_all(self) -> None:
        for key in sorted(self.held_keys):
            self.events.append(("up", key))
        self.held_keys.clear()
        self.release_count += 1
