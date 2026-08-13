from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from naruto_agent.core.contracts import ControlCommand
from naruto_agent.core.interfaces import InputBackend
from naruto_agent.runtime.clock import monotonic_ns


@dataclass(frozen=True, slots=True)
class SafetySnapshot:
    dry_run: bool
    live_input_opt_in: bool
    window_focused: bool
    calibration_valid: bool
    capture_fresh: bool
    emergency_stop_active: bool
    capture_frozen: bool = False
    policy_timed_out: bool = False
    character_recognized: bool = True
    action_rate_ok: bool = True
    emergency_stop_listener_active: bool = True


class SafetyGate:
    """Central live-action authorization. Policies must not bypass this gate."""

    def authorize_live_action(self, snapshot: SafetySnapshot) -> tuple[bool, str]:
        if snapshot.dry_run:
            return False, "dry_run"
        if not snapshot.live_input_opt_in:
            return False, "live_input_not_opted_in"
        if snapshot.emergency_stop_active:
            return False, "emergency_stop"
        if not snapshot.emergency_stop_listener_active:
            return False, "emergency_stop_listener_inactive"
        if not snapshot.window_focused:
            return False, "window_not_focused"
        if not snapshot.calibration_valid:
            return False, "invalid_calibration"
        if not snapshot.capture_fresh:
            return False, "stale_capture"
        if snapshot.capture_frozen:
            return False, "frozen_capture"
        if snapshot.policy_timed_out:
            return False, "policy_timeout"
        if not snapshot.character_recognized:
            return False, "character_unrecognized"
        if not snapshot.action_rate_ok:
            return False, "action_rate_limited"
        return True, "authorized"


@dataclass(frozen=True, slots=True)
class DispatchResult:
    executed: bool
    simulated: bool
    reason: str


class ActionScheduler:
    """The only policy-facing route from ControlCommand to an input backend."""

    def __init__(
        self,
        backend: InputBackend,
        *,
        max_batches_per_second: int = 15,
        gate: SafetyGate | None = None,
    ) -> None:
        if max_batches_per_second < 1:
            raise ValueError("max_batches_per_second must be positive")
        self._backend = backend
        self._limit = max_batches_per_second
        self._gate = gate or SafetyGate()
        self._recent_batches: deque[int] = deque()

    def _within_rate_limit(self, now_ns: int) -> bool:
        cutoff = now_ns - 1_000_000_000
        while self._recent_batches and self._recent_batches[0] <= cutoff:
            self._recent_batches.popleft()
        return len(self._recent_batches) < self._limit

    def dispatch(self, command: ControlCommand, snapshot: SafetySnapshot) -> DispatchResult:
        now_ns = monotonic_ns()
        rate_ok = self._within_rate_limit(now_ns)
        effective = SafetySnapshot(
            dry_run=snapshot.dry_run,
            live_input_opt_in=snapshot.live_input_opt_in,
            window_focused=snapshot.window_focused,
            calibration_valid=snapshot.calibration_valid,
            capture_fresh=snapshot.capture_fresh,
            emergency_stop_active=snapshot.emergency_stop_active,
            capture_frozen=snapshot.capture_frozen,
            policy_timed_out=snapshot.policy_timed_out,
            character_recognized=snapshot.character_recognized,
            action_rate_ok=snapshot.action_rate_ok and rate_ok,
            emergency_stop_listener_active=snapshot.emergency_stop_listener_active,
        )
        authorized, reason = self._gate.authorize_live_action(effective)
        if not self._backend.is_live:
            self._recent_batches.append(now_ns)
            self._backend.execute(command)
            return DispatchResult(executed=False, simulated=True, reason=reason)
        if not authorized:
            self._backend.release_all()
            return DispatchResult(executed=False, simulated=False, reason=reason)
        try:
            self._recent_batches.append(now_ns)
            self._backend.execute(command)
        except BaseException:
            self._backend.release_all()
            raise
        return DispatchResult(executed=True, simulated=False, reason="authorized")

    def close(self) -> None:
        self._backend.release_all()
