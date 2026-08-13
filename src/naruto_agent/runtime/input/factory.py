from __future__ import annotations

from collections.abc import Callable

from naruto_agent.config.models import EmulatorProfile
from naruto_agent.core.interfaces import InputBackend
from naruto_agent.runtime.input.dry_run import DryRunInputBackend
from naruto_agent.runtime.input.windows import WindowsInputBackend


def create_input_backend(
    *,
    live_input: bool = False,
    profile: EmulatorProfile | None = None,
    target_handle: int | None = None,
    focus_check: Callable[[int], bool] | None = None,
    session_indicator: Callable[[str], None] | None = None,
) -> InputBackend:
    """Factory boundary for a CLI ``--live-input`` flag; defaults to dry-run."""

    if not live_input:
        return DryRunInputBackend()
    if profile is None or target_handle is None or focus_check is None:
        raise ValueError("live input requires a profile, selected window, and focus checker")
    if session_indicator is None:
        raise ValueError("live input requires a visible session indicator callback")
    return WindowsInputBackend(
        profile=profile,
        target_handle=target_handle,
        focus_check=focus_check,
        live_input_opt_in=True,
        session_indicator=session_indicator,
    )
