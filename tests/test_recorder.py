import time
from pathlib import Path

import pytest

from naruto_agent.core.contracts import ControlCommand
from naruto_agent.core.enums import CharacterId
from naruto_agent.data.models import EpisodeManifest, QualityFlag
from naruto_agent.data.recorder import EpisodeRecorder, inspect_episode, validate_episode
from naruto_agent.runtime.capture.mock import MockCaptureBackend


def _recorder(root: Path) -> EpisodeRecorder:
    return EpisodeRecorder(
        root=root,
        controlled_character=CharacterId.TAKA_SASUKE,
        lineup=[CharacterId.TAKA_SASUKE, CharacterId.WHITE_MASK, CharacterId.PAIN],
        emulator_profile_id="mock",
        configuration={"capture": {}, "control": {}, "character": {}},
        max_raw_frames=4,
        code_commit=None,
    )


def test_episode_finalizes_and_validates_after_injected_exception(tmp_path: Path) -> None:
    recorder = _recorder(tmp_path)
    capture = MockCaptureBackend(frame_count=1)
    with pytest.raises(RuntimeError, match="injected"), recorder:
        capture.start()
        recorder.record_frame(next(capture.frames()))
        raise RuntimeError("injected")
    manifest = EpisodeManifest.model_validate_json(
        (recorder.episode_dir / "manifest.json").read_text(encoding="utf-8")
    )
    assert manifest.ended_at_utc is not None
    assert QualityFlag.INCOMPLETE_FINALIZATION in manifest.quality_flags
    assert validate_episode(recorder.episode_dir) == []


def test_recorder_rejects_non_monotonic_frames(tmp_path: Path) -> None:
    recorder = _recorder(tmp_path)
    capture = MockCaptureBackend(frame_count=1)
    capture.start()
    frame = next(capture.frames())
    recorder.record_frame(frame)
    with pytest.raises(ValueError, match="strictly monotonic"):
        recorder.record_frame(frame)
    recorder.abort(reason="test complete")


def test_episode_inspection_reports_counts(tmp_path: Path) -> None:
    recorder = _recorder(tmp_path)
    capture = MockCaptureBackend(frame_count=2)
    capture.start()
    for frame in capture.frames():
        recorder.record_frame(frame)
        recorder.record_control(
            ControlCommand(timestamp_ns=max(time.monotonic_ns(), frame.timestamp_ns + 1)),
            character_id=CharacterId.TAKA_SASUKE,
        )
    recorder.finalize()
    summary = inspect_episode(recorder.episode_dir)
    assert summary["frames"] == 2
    assert summary["control_intervals"] == 2
    assert summary["validation_errors"] == []


def test_checksum_tampering_is_detected(tmp_path: Path) -> None:
    recorder = _recorder(tmp_path)
    recorder.finalize()
    (recorder.episode_dir / "actions.jsonl").write_text("{}\n", encoding="utf-8")
    errors = validate_episode(recorder.episode_dir)
    assert any("checksum mismatch" in error for error in errors)
