import pytest

from naruto_agent.runtime.window import (
    AmbiguousWindowError,
    MockWindowLocator,
    WindowInfo,
    WindowNotFoundError,
    WindowQuery,
)


def _window(handle: int, title: str, process: str = "emulator.exe") -> WindowInfo:
    return WindowInfo(handle, title, handle + 100, process, 0, 0, 1280, 720, True)


def test_ambiguous_window_selection_is_explicit_and_deterministic() -> None:
    locator = MockWindowLocator([_window(2, "Practice B"), _window(1, "Practice A")])
    query = WindowQuery(title_substring="practice", minimum_width=800, minimum_height=450)
    assert [item.handle for item in locator.find(query)] == [1, 2]
    with pytest.raises(AmbiguousWindowError, match="handle=1"):
        locator.select(query)


def test_window_filtering_process_visibility_and_dimensions() -> None:
    locator = MockWindowLocator(
        [
            _window(1, "Game"),
            WindowInfo(2, "Game", 12, "other.exe", 0, 0, 1280, 720, True),
            WindowInfo(3, "Game", 13, "emulator.exe", 0, 0, 320, 180, True),
            WindowInfo(4, "Game", 14, "emulator.exe", 0, 0, 1280, 720, False),
        ]
    )
    selected = locator.select(
        WindowQuery(
            title_substring="game",
            process_name="emulator.exe",
            minimum_width=800,
            minimum_height=450,
        )
    )
    assert selected.handle == 1


def test_missing_window_is_an_explicit_error() -> None:
    with pytest.raises(WindowNotFoundError):
        MockWindowLocator([]).select(WindowQuery())
