from pathlib import Path

from naruto_agent.core.enums import ButtonAction, CharacterId, MovementDirection, StrategicIntent
from naruto_agent.data.recorder import inspect_episode
from naruto_agent.demo import dry_run_policy_output, placeholder_observation, run_mock_vertical_loop
from naruto_agent.runtime.capture.mock import MockCaptureBackend


def test_mock_vertical_loop_produces_valid_episode(tmp_path: Path) -> None:
    episode = run_mock_vertical_loop(tmp_path, frame_count=5)
    summary = inspect_episode(episode)
    assert summary["frames"] == 5
    assert summary["control_intervals"] == 5
    assert summary["validation_errors"] == []


def test_placeholder_observation_policy_is_explicitly_unknown_and_neutral() -> None:
    capture = MockCaptureBackend(frame_count=1)
    capture.start()
    observation = placeholder_observation(next(capture.frames()))
    output = dry_run_policy_output(observation)
    assert observation.active_character is CharacterId.UNKNOWN
    assert observation.confidence == {"placeholder": 0.0}
    assert output.strategic.intent is StrategicIntent.NEUTRAL
    assert output.control is not None
    assert output.control.movement is MovementDirection.NEUTRAL
    assert output.control.button is ButtonAction.NONE
