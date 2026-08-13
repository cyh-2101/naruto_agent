from __future__ import annotations

import ctypes
import sys
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import psutil


class WindowDiscoveryError(RuntimeError):
    """Base error for safe, explicit window discovery failures."""


class WindowNotFoundError(WindowDiscoveryError):
    pass


class AmbiguousWindowError(WindowDiscoveryError):
    pass


@dataclass(frozen=True, slots=True)
class WindowInfo:
    handle: int
    title: str
    process_id: int
    process_name: str | None
    left: int
    top: int
    width: int
    height: int
    visible: bool

    def __post_init__(self) -> None:
        if self.handle < 0 or self.process_id < 0:
            raise ValueError("window handle and process ID must be non-negative")
        if self.width < 0 or self.height < 0:
            raise ValueError("window dimensions must be non-negative")


@dataclass(frozen=True, slots=True)
class WindowQuery:
    title_substring: str | None = None
    process_name: str | None = None
    visible_only: bool = True
    minimum_width: int = 1
    minimum_height: int = 1

    def __post_init__(self) -> None:
        if self.minimum_width < 1 or self.minimum_height < 1:
            raise ValueError("minimum window dimensions must be positive")


@runtime_checkable
class WindowLocator(Protocol):
    def enumerate(self) -> list[WindowInfo]: ...

    def find(self, query: WindowQuery) -> list[WindowInfo]: ...

    def select(self, query: WindowQuery) -> WindowInfo: ...

    def is_focused(self, handle: int) -> bool: ...


def filter_windows(windows: list[WindowInfo], query: WindowQuery) -> list[WindowInfo]:
    title = query.title_substring.casefold() if query.title_substring else None
    process = query.process_name.casefold() if query.process_name else None
    matches = []
    for window in windows:
        if query.visible_only and not window.visible:
            continue
        if window.width < query.minimum_width or window.height < query.minimum_height:
            continue
        if title and title not in window.title.casefold():
            continue
        if process and (window.process_name is None or process != window.process_name.casefold()):
            continue
        matches.append(window)
    return sorted(
        matches,
        key=lambda item: (
            item.process_name.casefold() if item.process_name else "",
            item.title.casefold(),
            item.handle,
        ),
    )


def select_one(windows: list[WindowInfo], query: WindowQuery) -> WindowInfo:
    matches = filter_windows(windows, query)
    if not matches:
        raise WindowNotFoundError(
            "no window matched the configured title/process and minimum dimensions"
        )
    if len(matches) > 1:
        summary = "; ".join(
            f"handle={item.handle} title={item.title!r} process={item.process_name!r}"
            for item in matches
        )
        raise AmbiguousWindowError(f"window selection is ambiguous: {summary}")
    return matches[0]


class MockWindowLocator:
    def __init__(self, windows: list[WindowInfo], focused_handle: int | None = None) -> None:
        self._windows = list(windows)
        self._focused_handle = focused_handle

    def enumerate(self) -> list[WindowInfo]:
        return list(self._windows)

    def find(self, query: WindowQuery) -> list[WindowInfo]:
        return filter_windows(self._windows, query)

    def select(self, query: WindowQuery) -> WindowInfo:
        return select_one(self._windows, query)

    def is_focused(self, handle: int) -> bool:
        return self._focused_handle == handle

    def set_focused(self, handle: int | None) -> None:
        self._focused_handle = handle


if sys.platform == "win32":
    from ctypes import wintypes

    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    _user32.EnumWindows.argtypes = (_WNDENUMPROC, wintypes.LPARAM)
    _user32.EnumWindows.restype = wintypes.BOOL
    _user32.GetWindowTextLengthW.argtypes = (wintypes.HWND,)
    _user32.GetWindowTextLengthW.restype = ctypes.c_int
    _user32.GetWindowTextW.argtypes = (wintypes.HWND, wintypes.LPWSTR, ctypes.c_int)
    _user32.GetWindowTextW.restype = ctypes.c_int
    _user32.GetWindowRect.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.RECT))
    _user32.GetWindowRect.restype = wintypes.BOOL
    _user32.GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
    _user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    _user32.IsWindowVisible.argtypes = (wintypes.HWND,)
    _user32.IsWindowVisible.restype = wintypes.BOOL
    _user32.GetForegroundWindow.argtypes = ()
    _user32.GetForegroundWindow.restype = wintypes.HWND


class WindowsWindowLocator:
    """Top-level window discovery using documented Win32 user32 APIs."""

    def __init__(self) -> None:
        if sys.platform != "win32":
            raise RuntimeError("native window discovery requires Windows")

    def enumerate(self) -> list[WindowInfo]:
        windows: list[WindowInfo] = []

        def callback(hwnd: int, _lparam: int) -> bool:
            length = int(_user32.GetWindowTextLengthW(hwnd))
            buffer = ctypes.create_unicode_buffer(length + 1)
            _user32.GetWindowTextW(hwnd, buffer, len(buffer))
            rect = wintypes.RECT()
            if not _user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return True
            pid = wintypes.DWORD()
            _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            try:
                process_name = psutil.Process(int(pid.value)).name()
            except (psutil.Error, OSError):
                process_name = None
            windows.append(
                WindowInfo(
                    handle=int(hwnd),
                    title=buffer.value,
                    process_id=int(pid.value),
                    process_name=process_name,
                    left=int(rect.left),
                    top=int(rect.top),
                    width=max(0, int(rect.right - rect.left)),
                    height=max(0, int(rect.bottom - rect.top)),
                    visible=bool(_user32.IsWindowVisible(hwnd)),
                )
            )
            return True

        callback_ref = _WNDENUMPROC(callback)
        if not _user32.EnumWindows(callback_ref, 0):
            error = ctypes.get_last_error()
            if error:
                raise ctypes.WinError(error)
        return sorted(windows, key=lambda item: item.handle)

    def find(self, query: WindowQuery) -> list[WindowInfo]:
        return filter_windows(self.enumerate(), query)

    def select(self, query: WindowQuery) -> WindowInfo:
        return select_one(self.enumerate(), query)

    def is_focused(self, handle: int) -> bool:
        return int(_user32.GetForegroundWindow()) == handle
