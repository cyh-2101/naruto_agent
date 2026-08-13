from __future__ import annotations

import atexit
import hashlib
import json
import os
import subprocess
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TextIO
from uuid import UUID, uuid4

import numpy as np
from pydantic import BaseModel

from naruto_agent.core.contracts import ControlCommand, FramePacket
from naruto_agent.core.enums import CharacterId
from naruto_agent.data.models import (
    ControlStateInterval,
    EpisodeFile,
    EpisodeManifest,
    FrameIndexEvent,
    InputEvent,
    QualityFlag,
    SourceType,
)
from naruto_agent.runtime.clock import monotonic_ns


class EpisodeRecorder:
    """Crash-tolerant synchronized recorder with a bounded raw-frame fallback."""

    def __init__(
        self,
        *,
        root: Path,
        controlled_character: CharacterId,
        lineup: list[CharacterId],
        emulator_profile_id: str,
        configuration: Mapping[str, Any],
        source_type: SourceType = SourceType.SCRIPTED_AGENT,
        session_id: UUID | None = None,
        max_raw_frames: int = 300,
        timestamp_gap_ms: int = 250,
        code_commit: str | None = None,
    ) -> None:
        if controlled_character is CharacterId.UNKNOWN:
            raise ValueError("recording requires a selected controlled character")
        if max_raw_frames < 1 or timestamp_gap_ms < 1:
            raise ValueError("recording bounds must be positive")
        self.episode_id = uuid4()
        self.episode_dir = root / str(self.episode_id)
        if self.episode_dir.exists():
            raise FileExistsError(self.episode_dir)
        self.episode_dir.mkdir(parents=True)
        self._max_raw_frames = max_raw_frames
        self._timestamp_gap_ns = timestamp_gap_ms * 1_000_000
        self._frame_count = 0
        self._last_frame_timestamp = 0
        self._last_input_timestamp = 0
        self._last_action_end = 0
        self._closed = False
        self._frame_handle = self._open_jsonl("frame_index.jsonl")
        self._input_handle = self._open_jsonl("input_events.jsonl")
        self._action_handle = self._open_jsonl("actions.jsonl")
        hashes = {
            name: _stable_hash(value)
            for name, value in configuration.items()
        }
        started_ns = monotonic_ns()
        self.manifest = EpisodeManifest(
            schema_version=1,
            episode_id=self.episode_id,
            session_id=session_id or uuid4(),
            source_type=source_type,
            started_at_utc=datetime.now(UTC),
            started_monotonic_ns=started_ns,
            controlled_character=controlled_character,
            lineup=lineup,
            emulator_profile_id=emulator_profile_id,
            capture_config_hash=hashes.get("capture", _stable_hash({})),
            control_config_hash=hashes.get("control", _stable_hash({})),
            character_config_hash=hashes.get("character", _stable_hash({})),
            code_commit=(
                code_commit if code_commit is not None else discover_code_commit(Path.cwd())
            ),
            quality_flags=[QualityFlag.RAW_FRAME_FALLBACK],
            notes="Foundation bounded raw-frame fallback; no model/perception outputs recorded.",
        )
        self._write_manifest()
        atexit.register(self._finalize_on_process_exit)

    def _open_jsonl(self, name: str) -> TextIO:
        return (self.episode_dir / name).open("x", encoding="utf-8", newline="\n")

    def _append(self, handle: TextIO, model: BaseModel) -> None:
        handle.write(model.model_dump_json() + "\n")
        handle.flush()
        os.fsync(handle.fileno())

    def record_frame(self, frame: FramePacket) -> None:
        self._ensure_open()
        if frame.timestamp_ns <= self._last_frame_timestamp:
            raise ValueError("frame timestamps must be strictly monotonic")
        if (
            self._last_frame_timestamp
            and frame.timestamp_ns - self._last_frame_timestamp > self._timestamp_gap_ns
        ):
            self._flag(QualityFlag.TIMESTAMP_GAP)
        if frame.dropped_before:
            self._flag(QualityFlag.DROPPED_FRAMES)
        if self._frame_count >= self._max_raw_frames:
            self._flag(QualityFlag.DROPPED_FRAMES)
            raise RuntimeError("bounded raw-frame fallback reached max_raw_frames")
        relative = Path("frames") / f"{frame.frame_id:08d}.npy"
        destination = self.episode_dir / relative
        destination.parent.mkdir(exist_ok=True)
        if destination.exists():
            raise FileExistsError(f"raw frame is immutable and already exists: {relative}")
        np.save(destination, frame.image, allow_pickle=False)
        event = FrameIndexEvent(
            schema_version=1,
            frame_id=frame.frame_id,
            timestamp_ns=frame.timestamp_ns,
            duplicate=frame.duplicate,
            dropped_before=frame.dropped_before,
        )
        self._append(self._frame_handle, event)
        self._frame_count += 1
        self._last_frame_timestamp = frame.timestamp_ns

    def record_input(self, event: InputEvent) -> None:
        self._ensure_open()
        if event.timestamp_ns <= self._last_input_timestamp:
            raise ValueError("input timestamps must be strictly monotonic")
        self._append(self._input_handle, event)
        self._last_input_timestamp = event.timestamp_ns

    def record_control(self, command: ControlCommand, *, character_id: CharacterId) -> None:
        self._ensure_open()
        start_ns = max(command.timestamp_ns, self._last_action_end + 1)
        end_ns = start_ns + command.hold_ms * 1_000_000
        interval = ControlStateInterval(
            schema_version=1,
            start_ns=start_ns,
            end_ns=end_ns,
            movement=command.movement,
            button=command.button,
            character_id=character_id,
            source="dry_run",
            confidence=1.0,
        )
        self._append(self._action_handle, interval)
        self._last_action_end = end_ns

    def finalize(self, *, notes: str | None = None) -> EpisodeManifest:
        return self._finish(notes=notes)

    def abort(self, *, reason: str) -> EpisodeManifest:
        self._flag(QualityFlag.ABORTED)
        return self._finish(notes=f"Aborted: {reason}")

    def finalize_after_exception(self, error: BaseException) -> EpisodeManifest:
        self._flag(QualityFlag.INCOMPLETE_FINALIZATION)
        return self._finish(notes=f"Exception finalization: {type(error).__name__}: {error}")

    def _finish(self, *, notes: str | None) -> EpisodeManifest:
        if self._closed:
            return self.manifest
        for handle in (self._frame_handle, self._input_handle, self._action_handle):
            handle.flush()
            os.fsync(handle.fileno())
            handle.close()
        ended_ns = max(monotonic_ns(), self.manifest.started_monotonic_ns)
        files = []
        for role, name in (
            ("frame_index", "frame_index.jsonl"),
            ("input_events", "input_events.jsonl"),
            ("control_intervals", "actions.jsonl"),
        ):
            files.append(
                EpisodeFile(
                    role=role,
                    relative_path=name,
                    sha256=_file_sha256(self.episode_dir / name),
                )
            )
        for path in sorted((self.episode_dir / "frames").glob("*.npy")):
            files.append(
                EpisodeFile(
                    role="raw_frame",
                    relative_path=path.relative_to(self.episode_dir).as_posix(),
                    sha256=_file_sha256(path),
                )
            )
        self.manifest = self.manifest.model_copy(
            update={
                "ended_at_utc": datetime.now(UTC),
                "ended_monotonic_ns": ended_ns,
                "files": files,
                "notes": notes or self.manifest.notes,
            }
        )
        self._closed = True
        self._write_manifest()
        atexit.unregister(self._finalize_on_process_exit)
        return self.manifest

    def _finalize_on_process_exit(self) -> None:
        if self._closed:
            return
        try:
            self._flag(QualityFlag.INCOMPLETE_FINALIZATION)
            self._finish(notes="Process-exit finalization; inspect episode quality before use.")
        except BaseException:
            # Interpreter teardown can make dependencies unavailable. The atomic partial
            # manifest remains for the explicit recovery command.
            return

    def _flag(self, flag: QualityFlag) -> None:
        if flag not in self.manifest.quality_flags:
            self.manifest = self.manifest.model_copy(
                update={"quality_flags": [*self.manifest.quality_flags, flag]}
            )
            self._write_manifest()

    def _write_manifest(self) -> None:
        target = self.episode_dir / "manifest.json"
        temporary = self.episode_dir / "manifest.json.tmp"
        temporary.write_text(self.manifest.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(target)

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("episode recorder is finalized")

    def __enter__(self) -> EpisodeRecorder:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        _traceback: object,
    ) -> None:
        if exc is None:
            self.finalize()
        else:
            self.finalize_after_exception(exc)


def validate_episode(episode_dir: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = episode_dir / "manifest.json"
    try:
        manifest = EpisodeManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"manifest invalid: {exc}"]
    if manifest.ended_at_utc is None or manifest.ended_monotonic_ns is None:
        errors.append("episode is not finalized")
    for item in manifest.files:
        path = episode_dir / item.relative_path
        if not path.is_file():
            errors.append(f"missing file: {item.relative_path}")
        elif item.sha256 and _file_sha256(path) != item.sha256:
            errors.append(f"checksum mismatch: {item.relative_path}")
    for name, model, field in (
        ("frame_index.jsonl", FrameIndexEvent, "timestamp_ns"),
        ("input_events.jsonl", InputEvent, "timestamp_ns"),
        ("actions.jsonl", ControlStateInterval, "start_ns"),
    ):
        path = episode_dir / name
        previous = 0
        try:
            with path.open("r", encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, 1):
                    parsed = model.model_validate_json(line)
                    timestamp = int(getattr(parsed, field))
                    if timestamp <= previous:
                        errors.append(f"{name}:{line_number} timestamp is not strictly monotonic")
                    previous = timestamp
        except (OSError, ValueError) as exc:
            errors.append(f"{name} invalid: {exc}")
    frames_dir = episode_dir / "frames"
    indexed_frames = _line_count(episode_dir / "frame_index.jsonl")
    stored_frames = len(list(frames_dir.glob("*.npy"))) if frames_dir.exists() else 0
    if indexed_frames != stored_frames:
        errors.append(f"frame count mismatch: index={indexed_frames}, stored={stored_frames}")
    return errors


def inspect_episode(episode_dir: Path) -> dict[str, Any]:
    manifest = EpisodeManifest.model_validate_json(
        (episode_dir / "manifest.json").read_text(encoding="utf-8")
    )
    return {
        "episode_id": str(manifest.episode_id),
        "controlled_character": manifest.controlled_character.value,
        "finalized": manifest.ended_at_utc is not None,
        "frames": _line_count(episode_dir / "frame_index.jsonl"),
        "input_events": _line_count(episode_dir / "input_events.jsonl"),
        "control_intervals": _line_count(episode_dir / "actions.jsonl"),
        "quality_flags": [flag.value for flag in manifest.quality_flags],
        "validation_errors": validate_episode(episode_dir),
    }


def recover_episode(episode_dir: Path, *, reason: str) -> EpisodeManifest:
    """Finalize an unclosed on-disk episode after a previous process crash."""

    manifest_path = episode_dir / "manifest.json"
    manifest = EpisodeManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    if manifest.ended_at_utc is not None:
        raise ValueError("episode is already finalized")
    flags = list(manifest.quality_flags)
    if QualityFlag.INCOMPLETE_FINALIZATION not in flags:
        flags.append(QualityFlag.INCOMPLETE_FINALIZATION)
    files = []
    for name, role in (
        ("frame_index.jsonl", "frame_index"),
        ("input_events.jsonl", "input_events"),
        ("actions.jsonl", "control_intervals"),
    ):
        path = episode_dir / name
        if path.is_file():
            files.append(EpisodeFile(role=role, relative_path=name, sha256=_file_sha256(path)))
    for path in sorted((episode_dir / "frames").glob("*.npy")):
        files.append(
            EpisodeFile(
                role="raw_frame",
                relative_path=path.relative_to(episode_dir).as_posix(),
                sha256=_file_sha256(path),
            )
        )
    recovered = manifest.model_copy(
        update={
            "ended_at_utc": datetime.now(UTC),
            "ended_monotonic_ns": max(monotonic_ns(), manifest.started_monotonic_ns),
            "files": files,
            "quality_flags": flags,
            "notes": f"Recovered after crash: {reason}",
        }
    )
    temporary = episode_dir / "manifest.json.tmp"
    temporary.write_text(recovered.model_dump_json(indent=2), encoding="utf-8")
    temporary.replace(manifest_path)
    return recovered


def discover_code_commit(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def _stable_hash(value: Any) -> str:
    serialized = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _line_count(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return sum(1 for _line in handle)
    except FileNotFoundError:
        return 0
