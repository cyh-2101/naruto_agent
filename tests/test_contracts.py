import time

import numpy as np
import pytest

from naruto_agent.core.contracts import ControlCommand, FramePacket, Point2D
from naruto_agent.core.enums import ButtonAction, MovementDirection
from naruto_agent.runtime.capture.mock import MockCaptureBackend
from naruto_agent.runtime.input.mock import MockInputBackend
from naruto_agent.runtime.safety import SafetyGate, SafetySnapshot


def test_point_rejects_non_normalized_coordinates() -> None:
    with pytest.raises(ValueError):
        Point2D(x=1.1, y=0.5)


def test_frame_packet_validates_shape_and_dtype() -> None:
    frame = FramePacket(
        frame_id=0,
        timestamp_ns=time.monotonic_ns(),
        source_id="test",
        image=np.zeros((10, 20, 3), dtype=np.uint8),
    )
    assert frame.image.shape == (10, 20, 3)


def test_mock_capture_timestamps_are_monotonic() -> None:
    backend = MockCaptureBackend(frame_count=5)
    backend.start()
    frames = list(backend.frames())
    backend.stop()
    timestamps = [frame.timestamp_ns for frame in frames]
    assert timestamps == sorted(timestamps)
    assert len(set(timestamps)) == len(timestamps)


def test_mock_input_never_reports_live() -> None:
    backend = MockInputBackend()
    command = ControlCommand(
        timestamp_ns=time.monotonic_ns(),
        movement=MovementDirection.RIGHT,
        button=ButtonAction.NORMAL_ATTACK,
        hold_ms=100,
        source="test",
    )
    backend.execute(command)
    assert not backend.is_live
    assert backend.commands == [command]
    backend.release_all()
    assert backend.release_count == 1


@pytest.mark.parametrize(
    ("snapshot", "reason"),
    [
        (
            SafetySnapshot(True, False, True, True, True, False),
            "dry_run",
        ),
        (
            SafetySnapshot(False, False, True, True, True, False),
            "live_input_not_opted_in",
        ),
        (
            SafetySnapshot(False, True, True, True, True, True),
            "emergency_stop",
        ),
        (
            SafetySnapshot(False, True, False, True, True, False),
            "window_not_focused",
        ),
        (
            SafetySnapshot(False, True, True, False, True, False),
            "invalid_calibration",
        ),
        (
            SafetySnapshot(False, True, True, True, False, False),
            "stale_capture",
        ),
    ],
)
def test_safety_gate_rejects_unsafe_state(snapshot: SafetySnapshot, reason: str) -> None:
    authorized, actual_reason = SafetyGate().authorize_live_action(snapshot)
    assert not authorized
    assert actual_reason == reason


def test_safety_gate_authorizes_only_complete_live_state() -> None:
    snapshot = SafetySnapshot(
        dry_run=False,
        live_input_opt_in=True,
        window_focused=True,
        calibration_valid=True,
        capture_fresh=True,
        emergency_stop_active=False,
    )
    assert SafetyGate().authorize_live_action(snapshot) == (True, "authorized")
