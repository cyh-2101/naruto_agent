import time

import pytest

from naruto_agent.core.contracts import ControlCommand
from naruto_agent.runtime.input.emergency import EmergencyStop
from naruto_agent.runtime.input.factory import create_input_backend
from naruto_agent.runtime.input.mock import MockInputBackend
from naruto_agent.runtime.safety import ActionScheduler, SafetySnapshot


def _snapshot(**overrides: bool) -> SafetySnapshot:
    values = {
        "dry_run": True,
        "live_input_opt_in": False,
        "window_focused": False,
        "calibration_valid": False,
        "capture_fresh": True,
        "emergency_stop_active": False,
    }
    values.update(overrides)
    return SafetySnapshot(**values)


def test_mock_held_key_cleanup() -> None:
    backend = MockInputBackend()
    backend.key_down("A")
    backend.key_down("B")
    backend.release_all()
    assert not backend.held_keys
    assert backend.events[-2:] == [("up", "A"), ("up", "B")]


def test_emergency_stop_transition_releases_all_keys() -> None:
    backend = MockInputBackend()
    backend.key_down("A")
    stop = EmergencyStop(backend.release_all)
    stop.trigger()
    assert stop.active
    assert not backend.held_keys
    assert backend.release_count == 1


def test_scheduler_default_path_is_simulation_only() -> None:
    backend = MockInputBackend()
    scheduler = ActionScheduler(backend)
    command = ControlCommand(timestamp_ns=time.monotonic_ns(), source="test")
    result = scheduler.dispatch(command, _snapshot())
    assert result.simulated
    assert not result.executed
    assert backend.commands == [command]


def test_input_factory_defaults_to_non_live_backend() -> None:
    backend = create_input_backend()
    assert not backend.is_live


def test_live_input_factory_requires_every_prerequisite() -> None:
    with pytest.raises(ValueError, match="profile"):
        create_input_backend(live_input=True)


class FailingLiveBackend(MockInputBackend):
    @property
    def is_live(self) -> bool:
        return True

    def execute(self, command: ControlCommand) -> None:
        self.key_down("A")
        raise RuntimeError("injected")


def test_scheduler_releases_held_keys_after_live_exception() -> None:
    backend = FailingLiveBackend()
    scheduler = ActionScheduler(backend)
    safe = _snapshot(
        dry_run=False,
        live_input_opt_in=True,
        window_focused=True,
        calibration_valid=True,
    )
    with pytest.raises(RuntimeError, match="injected"):
        scheduler.dispatch(ControlCommand(timestamp_ns=time.monotonic_ns()), safe)
    assert not backend.held_keys


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"capture_frozen": True}, "dry_run"),
        (
            {
                "dry_run": False,
                "live_input_opt_in": True,
                "window_focused": True,
                "calibration_valid": True,
                "capture_frozen": True,
            },
            "frozen_capture",
        ),
        (
            {
                "dry_run": False,
                "live_input_opt_in": True,
                "window_focused": True,
                "calibration_valid": True,
                "policy_timed_out": True,
            },
            "policy_timeout",
        ),
        (
            {
                "dry_run": False,
                "live_input_opt_in": True,
                "window_focused": True,
                "calibration_valid": True,
                "character_recognized": False,
            },
            "character_unrecognized",
        ),
    ],
)
def test_extended_safety_rejections(overrides: dict[str, bool], reason: str) -> None:
    backend = MockInputBackend()
    result = ActionScheduler(backend).dispatch(
        ControlCommand(timestamp_ns=time.monotonic_ns()), _snapshot(**overrides)
    )
    assert result.reason == reason
