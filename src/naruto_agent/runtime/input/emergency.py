from __future__ import annotations

import importlib
import threading
from collections.abc import Callable


class EmergencyStop:
    """Thread-safe latch whose transition immediately invokes key cleanup."""

    def __init__(self, release_all: Callable[[], None]) -> None:
        self._release_all = release_all
        self._active = threading.Event()
        self._listener: object | None = None

    @property
    def active(self) -> bool:
        return self._active.is_set()

    @property
    def listener_active(self) -> bool:
        if self._listener is None:
            return False
        is_alive = getattr(self._listener, "is_alive", None)
        return bool(is_alive()) if callable(is_alive) else False

    def trigger(self) -> None:
        self._active.set()
        self._release_all()

    def reset_for_new_session(self) -> None:
        self._active.clear()

    def start_hotkey_listener(self, hotkey: str) -> None:
        if not hotkey.strip():
            raise ValueError("emergency-stop hotkey cannot be blank")
        try:
            keyboard = importlib.import_module("pynput.keyboard")
        except ImportError as exc:
            raise RuntimeError("pynput is required for the emergency-stop listener") from exc
        expected = hotkey.casefold()

        def on_press(key: object) -> None:
            char = getattr(key, "char", None)
            rendered = str(char if char is not None else key).removeprefix("Key.").casefold()
            if rendered == expected:
                self.trigger()

        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        self._listener = listener
        if not self.listener_active:
            self.stop_listener()
            raise RuntimeError("emergency-stop listener failed to start")

    def stop_listener(self) -> None:
        if self._listener is not None:
            stop = getattr(self._listener, "stop", None)
            if callable(stop):
                stop()
        self._listener = None
