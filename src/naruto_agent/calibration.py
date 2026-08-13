from __future__ import annotations

from pathlib import Path

import yaml

from naruto_agent.config.loader import load_emulator_profile
from naruto_agent.config.models import EmulatorProfile
from naruto_agent.runtime.window import WindowInfo


def normalized_region(
    *, left: int, top: int, right: int, bottom: int, width: int, height: int
) -> tuple[float, float, float, float]:
    if width < 1 or height < 1:
        raise ValueError("reference dimensions must be positive")
    if min(left, top) < 0 or right <= left or bottom <= top:
        raise ValueError("region must have positive area and non-negative coordinates")
    if right > width or bottom > height:
        raise ValueError("region exceeds the reference dimensions")
    return (left / width, top / height, right / width, bottom / height)


def build_local_profile(
    *,
    profile_id: str,
    window: WindowInfo,
    crop_pixels: tuple[int, int, int, int] | None,
    movement: dict[str, str | None],
    buttons: dict[str, str | None],
    emergency_stop: str | None,
    ui_regions: dict[str, tuple[float, float, float, float] | None],
    verified: bool = False,
) -> EmulatorProfile:
    payload = {
        "schema_version": 1,
        "profile_version": 1,
        "profile_id": profile_id,
        "verified": verified,
        "window": {
            "title_contains": window.title,
            "process_name": window.process_name,
            "minimum_width": window.width,
            "minimum_height": window.height,
        },
        "capture": {
            "backend": "dxcam",
            "crop_pixels": crop_pixels,
            "target_fps": 30,
            "queue_size": 8,
            "frozen_frame_threshold": 6,
        },
        "ui_regions": ui_regions,
        "controls": {
            "movement": movement,
            "buttons": buttons,
            "emergency_stop": emergency_stop,
        },
        "notes": "Local CLI-generated profile; mark verified only after manual validation.",
    }
    return EmulatorProfile.model_validate(payload)


def save_local_profile(profile: EmulatorProfile, destination: Path) -> Path:
    resolved = destination.resolve()
    if "configs" not in resolved.parts or "local" not in resolved.parts:
        raise ValueError("real calibration profiles must be stored under configs/local")
    if resolved.name.endswith(".example.yaml"):
        raise ValueError("example profiles are immutable")
    if resolved.exists():
        raise FileExistsError(f"refusing to overwrite existing profile: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(
        yaml.safe_dump(profile.model_dump(mode="json"), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return resolved


def validate_local_profile(path: Path, *, require_live_ready: bool = False) -> EmulatorProfile:
    profile = load_emulator_profile(path)
    if require_live_ready:
        profile.assert_live_ready()
    return profile
