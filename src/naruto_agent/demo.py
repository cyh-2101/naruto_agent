from __future__ import annotations

import tempfile
from pathlib import Path

from naruto_agent.core.contracts import (
    ControlCommand,
    FramePacket,
    PerceptionState,
    PolicyOutput,
    StrategicDecision,
)
from naruto_agent.core.enums import (
    ButtonAction,
    CharacterId,
    MovementDirection,
    StrategicIntent,
)
from naruto_agent.data.recorder import EpisodeRecorder, inspect_episode
from naruto_agent.runtime.capture.mock import MockCaptureBackend
from naruto_agent.runtime.clock import monotonic_ns
from naruto_agent.runtime.input.mock import MockInputBackend
from naruto_agent.runtime.safety import ActionScheduler, SafetySnapshot


def placeholder_observation(frame: FramePacket) -> PerceptionState:
    """Explicitly unknown observation for interface testing; not game perception."""

    return PerceptionState(timestamp_ns=frame.timestamp_ns, confidence={"placeholder": 0.0})


def dry_run_policy_output(observation: PerceptionState) -> PolicyOutput:
    """Fail-safe neutral output used only by the mock architecture demo."""

    timestamp_ns = max(monotonic_ns(), observation.timestamp_ns + 1)
    strategic = StrategicDecision(
        timestamp_ns=timestamp_ns,
        intent=StrategicIntent.NEUTRAL,
        confidence=0.0,
        reason_code="placeholder_observation",
    )
    command = ControlCommand(
        timestamp_ns=timestamp_ns,
        movement=MovementDirection.NEUTRAL,
        button=ButtonAction.NONE,
        hold_ms=0,
        source="placeholder_observation_policy",
    )
    return PolicyOutput(
        timestamp_ns=timestamp_ns,
        strategic=strategic,
        macro=None,
        control=command,
        confidence=0.0,
    )


def run_mock_vertical_loop(output_root: Path | None = None, frame_count: int = 6) -> Path:
    """Safe vertical slice: synthetic frames, neutral placeholder, mock input, recorder."""

    if frame_count < 1:
        raise ValueError("frame_count must be positive")
    root = output_root or Path(tempfile.mkdtemp(prefix="naruto-agent-mock-"))
    capture = MockCaptureBackend(frame_count=frame_count, duplicate_every=3)
    backend = MockInputBackend()
    scheduler = ActionScheduler(backend)
    recorder = EpisodeRecorder(
        root=root,
        controlled_character=CharacterId.TAKA_SASUKE,
        lineup=[CharacterId.TAKA_SASUKE, CharacterId.WHITE_MASK, CharacterId.PAIN],
        emulator_profile_id="mock-unconfigured",
        configuration={
            "capture": {"backend": "mock", "frame_count": frame_count},
            "control": {"backend": "mock", "dry_run": True},
            "character": {"character_id": CharacterId.TAKA_SASUKE.value, "verified": False},
        },
    )
    snapshot = SafetySnapshot(
        dry_run=True,
        live_input_opt_in=False,
        window_focused=False,
        calibration_valid=False,
        capture_fresh=True,
        emergency_stop_active=False,
    )
    capture.start()
    try:
        for frame in capture.frames():
            recorder.record_frame(frame)
            observation = placeholder_observation(frame)
            policy_output = dry_run_policy_output(observation)
            assert policy_output.control is not None
            command = policy_output.control
            result = scheduler.dispatch(command, snapshot)
            if not result.simulated or result.executed:
                raise RuntimeError("mock vertical loop left its dry-run boundary")
            recorder.record_control(command, character_id=CharacterId.TAKA_SASUKE)
        recorder.finalize(notes="Validated mock vertical loop; no OS input or game used.")
    except BaseException as exc:
        recorder.finalize_after_exception(exc)
        raise
    finally:
        capture.stop()
        scheduler.close()
    summary = inspect_episode(recorder.episode_dir)
    if summary["validation_errors"]:
        raise RuntimeError(f"mock episode validation failed: {summary['validation_errors']}")
    return recorder.episode_dir
