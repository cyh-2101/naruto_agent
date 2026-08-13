from __future__ import annotations

import atexit
import contextlib
import ctypes
import sys
import time
from collections.abc import Callable, Mapping

from naruto_agent.config.models import EmulatorProfile
from naruto_agent.core.contracts import ControlCommand
from naruto_agent.core.enums import ButtonAction, MovementDirection
from naruto_agent.runtime.input.emergency import EmergencyStop

_NAMED_VIRTUAL_KEYS = {
    "backspace": 0x08,
    "tab": 0x09,
    "enter": 0x0D,
    "shift": 0x10,
    "ctrl": 0x11,
    "alt": 0x12,
    "escape": 0x1B,
    "esc": 0x1B,
    "space": 0x20,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
}
_NAMED_VIRTUAL_KEYS.update({f"f{index}": 0x6F + index for index in range(1, 13)})


if sys.platform == "win32":
    from ctypes import wintypes

    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _INPUT_KEYBOARD = 1
    _KEYEVENTF_KEYUP = 0x0002

    class _KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.c_void_p),
        ]

    class _INPUT_UNION(ctypes.Union):
        _fields_ = [("ki", _KEYBDINPUT)]

    class _INPUT(ctypes.Structure):
        _anonymous_ = ("union",)
        _fields_ = [("type", wintypes.DWORD), ("union", _INPUT_UNION)]

    _user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(_INPUT), ctypes.c_int)
    _user32.SendInput.restype = wintypes.UINT


def _virtual_key(key: str) -> int:
    normalized = key.strip().casefold()
    if normalized in _NAMED_VIRTUAL_KEYS:
        return _NAMED_VIRTUAL_KEYS[normalized]
    if len(key) == 1 and key.isascii() and key.isalnum():
        return ord(key.upper())
    raise ValueError(f"unsupported normal-key binding: {key!r}")


class WindowsInputBackend:
    """Explicitly opted-in SendInput backend with focus and emergency-stop enforcement."""

    def __init__(
        self,
        *,
        profile: EmulatorProfile,
        target_handle: int,
        focus_check: Callable[[int], bool],
        live_input_opt_in: bool,
        session_indicator: Callable[[str], None],
    ) -> None:
        if sys.platform != "win32":
            raise RuntimeError("live normal-key input requires native Windows")
        if not live_input_opt_in:
            raise PermissionError("live input requires the explicit --live-input opt-in")
        profile.assert_live_ready()
        if not focus_check(target_handle):
            raise PermissionError("selected emulator window must be focused before live activation")
        bindings = [
            *profile.controls.movement.values(),
            *profile.controls.buttons.values(),
            profile.controls.emergency_stop,
        ]
        for binding in bindings:
            assert binding is not None
            _virtual_key(binding)
        self._target_handle = target_handle
        self._focus_check = focus_check
        self._held_keys: set[str] = set()
        self._closed = False
        self._movement = dict(profile.controls.movement)
        self._buttons = dict(profile.controls.buttons)
        self.emergency_stop = EmergencyStop(self.release_all)
        assert profile.controls.emergency_stop is not None
        self.emergency_stop.start_hotkey_listener(profile.controls.emergency_stop)
        try:
            session_indicator(
                "LIVE INPUT ACTIVE: "
                f"profile={profile.profile_id} window_handle={target_handle} "
                f"emergency_stop={profile.controls.emergency_stop}"
            )
        except BaseException:
            self.emergency_stop.stop_listener()
            raise
        atexit.register(self.release_all)

    @property
    def is_live(self) -> bool:
        return True

    @property
    def held_keys(self) -> frozenset[str]:
        return frozenset(self._held_keys)

    def _ensure_action_safe(self) -> None:
        if self._closed:
            raise RuntimeError("input backend is closed")
        if self.emergency_stop.active:
            self.release_all()
            raise PermissionError("emergency stop is active")
        if not self.emergency_stop.listener_active:
            self.release_all()
            raise PermissionError("emergency-stop listener is not active")
        if not self._focus_check(self._target_handle):
            self.release_all()
            raise PermissionError("selected emulator window is not focused")

    def _send(self, key: str, *, key_up: bool) -> None:
        virtual_key = _virtual_key(key)
        flags = _KEYEVENTF_KEYUP if key_up else 0
        event = _INPUT(
            type=_INPUT_KEYBOARD,
            ki=_KEYBDINPUT(
                wVk=virtual_key,
                wScan=0,
                dwFlags=flags,
                time=0,
                dwExtraInfo=None,
            ),
        )
        sent = int(_user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(_INPUT)))
        if sent != 1:
            raise ctypes.WinError(ctypes.get_last_error())

    def key_down(self, key: str) -> None:
        self._ensure_action_safe()
        if key not in self._held_keys:
            self._send(key, key_up=False)
            self._held_keys.add(key)

    def key_up(self, key: str) -> None:
        if key in self._held_keys:
            self._send(key, key_up=True)
            self._held_keys.discard(key)

    def timed_press(self, key: str, duration_ms: int) -> None:
        if duration_ms < 0:
            raise ValueError("duration_ms must be non-negative")
        self.key_down(key)
        try:
            time.sleep(duration_ms / 1000)
        finally:
            self.key_up(key)

    def execute(self, command: ControlCommand) -> None:
        self._ensure_action_safe()
        movement_keys = self._keys_for_movement(command.movement)
        try:
            for key in movement_keys:
                self.key_down(key)
            if command.button is not ButtonAction.NONE:
                button_key = self._buttons.get(command.button.value)
                if not button_key:
                    raise ValueError(f"no key binding for {command.button.value}")
                self.timed_press(button_key, command.hold_ms)
            elif command.hold_ms:
                time.sleep(command.hold_ms / 1000)
        finally:
            for key in reversed(movement_keys):
                self.key_up(key)

    def _keys_for_movement(self, movement: MovementDirection) -> list[str]:
        names: Mapping[MovementDirection, tuple[str, ...]] = {
            MovementDirection.NEUTRAL: (),
            MovementDirection.UP: ("up",),
            MovementDirection.DOWN: ("down",),
            MovementDirection.LEFT: ("left",),
            MovementDirection.RIGHT: ("right",),
            MovementDirection.UP_LEFT: ("up", "left"),
            MovementDirection.UP_RIGHT: ("up", "right"),
            MovementDirection.DOWN_LEFT: ("down", "left"),
            MovementDirection.DOWN_RIGHT: ("down", "right"),
        }
        keys = [self._movement.get(name) for name in names[movement]]
        if any(key is None for key in keys):
            raise ValueError(f"movement {movement.value} has incomplete bindings")
        return [key for key in keys if key is not None]

    def release_all(self) -> None:
        for key in sorted(self._held_keys):
            with contextlib.suppress(OSError):
                self._send(key, key_up=True)
        self._held_keys.clear()

    def close(self) -> None:
        self.release_all()
        self.emergency_stop.stop_listener()
        self._closed = True

    def __enter__(self) -> WindowsInputBackend:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()
