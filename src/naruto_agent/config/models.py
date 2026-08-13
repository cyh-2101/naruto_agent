from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from naruto_agent.core.enums import ButtonAction, CharacterId, MovementDirection


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SkillConfig(StrictModel):
    verified: bool = False
    press_ms: int | None = Field(default=None, ge=0)
    recovery_ms: int | None = Field(default=None, ge=0)
    variants: list[str] = Field(default_factory=list)


class PreferredDistance(StrictModel):
    close: float | None = Field(default=None, ge=0.0, le=1.0)
    medium: float | None = Field(default=None, ge=0.0, le=1.0)
    far: float | None = Field(default=None, ge=0.0, le=1.0)


class CharacterVisualConfig(StrictModel):
    identity_templates: list[str] = Field(default_factory=list)
    animation_templates: dict[str, list[str] | str] = Field(default_factory=dict)


class CharacterActionSpace(StrictModel):
    movement: list[MovementDirection]
    buttons: list[ButtonAction]


class CharacterConfig(StrictModel):
    schema_version: Literal[1]
    character_id: CharacterId
    display_name: str
    status: Literal[
        "declared",
        "input_calibrated",
        "timing_calibrated",
        "visual_calibrated",
        "script_verified",
        "policy_ready",
    ]
    verified: bool
    lineup_slot: int = Field(ge=1)
    adapter_key: str
    visual: CharacterVisualConfig
    action_space: CharacterActionSpace
    skills: dict[str, SkillConfig]
    preferred_distance: PreferredDistance
    macros: list[str]
    combo_graphs: dict[str, Any]
    evaluation_rules: dict[str, Any]
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def reject_unknown_character(self) -> CharacterConfig:
        if self.character_id is CharacterId.UNKNOWN:
            raise ValueError("UNKNOWN cannot be used for a configured controlled character")
        if self.verified and any(not skill.verified for skill in self.skills.values()):
            raise ValueError("a verified character cannot contain unverified skill entries")
        return self


class WindowProfile(StrictModel):
    title_contains: str | None = None
    process_name: str | None = None
    minimum_width: int = Field(default=800, gt=0)
    minimum_height: int = Field(default=450, gt=0)

    @model_validator(mode="after")
    def require_a_selector(self) -> WindowProfile:
        if not self.title_contains and not self.process_name:
            return self
        if self.title_contains is not None and not self.title_contains.strip():
            raise ValueError("title_contains cannot be blank")
        if self.process_name is not None and not self.process_name.strip():
            raise ValueError("process_name cannot be blank")
        return self


class CaptureProfile(StrictModel):
    backend: Literal["auto", "dxcam", "mock"] = "auto"
    crop_pixels: tuple[int, int, int, int] | None = None
    target_fps: int = Field(default=30, ge=1, le=240)
    queue_size: int = Field(default=8, ge=1, le=1024)
    frozen_frame_threshold: int = Field(default=6, ge=1)

    @model_validator(mode="after")
    def validate_crop(self) -> CaptureProfile:
        if self.crop_pixels is not None:
            left, top, right, bottom = self.crop_pixels
            if min(left, top) < 0 or right <= left or bottom <= top:
                raise ValueError("crop_pixels must be non-negative (left, top, right, bottom)")
        return self


class ControlProfile(StrictModel):
    movement: dict[str, str | None]
    buttons: dict[str, str | None]
    emergency_stop: str | None = None

    @model_validator(mode="after")
    def validate_normal_keys(self) -> ControlProfile:
        bindings = {
            **{f"movement.{name}": key for name, key in self.movement.items()},
            **{f"buttons.{name}": key for name, key in self.buttons.items()},
            "emergency_stop": self.emergency_stop,
        }
        for name, key in bindings.items():
            if key is not None and not _is_supported_normal_key(key):
                raise ValueError(f"{name} is not a supported normal-key binding: {key!r}")
        return self

    def missing_live_bindings(self) -> tuple[str, ...]:
        required_movement = ("up", "down", "left", "right")
        required_buttons = (
            "normal_attack",
            "skill_1",
            "skill_2",
            "ultimate",
            "substitution",
            "secret_scroll",
            "summon",
        )
        missing = [f"movement.{name}" for name in required_movement if not self.movement.get(name)]
        missing.extend(f"buttons.{name}" for name in required_buttons if not self.buttons.get(name))
        if not self.emergency_stop:
            missing.append("emergency_stop")
        return tuple(missing)


class EmulatorProfile(StrictModel):
    schema_version: Literal[1]
    profile_version: int = Field(default=1, ge=1)
    profile_id: str = Field(min_length=1)
    verified: bool
    window: WindowProfile
    capture: CaptureProfile
    ui_regions: dict[str, tuple[float, float, float, float] | None]
    controls: ControlProfile
    notes: str | None = None

    @model_validator(mode="after")
    def validate_regions_and_live_state(self) -> EmulatorProfile:
        if not self.profile_id.strip():
            raise ValueError("profile_id cannot be blank")
        for name, region in self.ui_regions.items():
            if region is None:
                continue
            left, top, right, bottom = region
            if not all(0.0 <= value <= 1.0 for value in region):
                raise ValueError(f"ui_regions.{name} must use normalized coordinates")
            if right <= left or bottom <= top:
                raise ValueError(f"ui_regions.{name} must have positive area")
        if self.verified:
            if not self.window.title_contains and not self.window.process_name:
                raise ValueError("verified profiles require a window selector")
            missing = self.controls.missing_live_bindings()
            if missing:
                raise ValueError(
                    "verified profiles require all live controls: " + ", ".join(missing)
                )
        return self

    def assert_live_ready(self) -> None:
        if not self.verified:
            raise ValueError("profile is not verified for live input")
        missing = self.controls.missing_live_bindings()
        if missing:
            raise ValueError("profile has missing live bindings: " + ", ".join(missing))


class ProjectPaths(StrictModel):
    data_root: Path
    artifact_root: Path


class RuntimeConfig(StrictModel):
    dry_run: bool = True
    live_input_enabled: bool = False
    require_focus: bool = True
    release_keys_on_error: bool = True
    frame_stale_after_ms: int = Field(default=250, ge=1)
    max_action_batches_per_second: int = Field(default=15, ge=1, le=60)
    emergency_stop_key: str | None = None

    @model_validator(mode="after")
    def preserve_safe_defaults(self) -> RuntimeConfig:
        if self.live_input_enabled and self.dry_run:
            raise ValueError("live_input_enabled conflicts with dry_run")
        if self.live_input_enabled and not self.emergency_stop_key:
            raise ValueError("live input requires an emergency_stop_key")
        return self


class ProjectIdentity(StrictModel):
    name: str
    mode: str
    data_root: Path
    artifact_root: Path


class ObservationConfig(StrictModel):
    history_ms: int = Field(ge=1)
    structured_state_enabled: bool
    visual_latent_enabled: bool


class LoggingConfig(StrictModel):
    level: str
    structured: bool


class BaseConfig(StrictModel):
    schema_version: Literal[1]
    project: ProjectIdentity
    runtime: RuntimeConfig
    observation: ObservationConfig
    logging: LoggingConfig


_NAMED_NORMAL_KEYS = {
    "alt",
    "backspace",
    "ctrl",
    "down",
    "enter",
    "esc",
    "escape",
    "left",
    "right",
    "shift",
    "space",
    "tab",
    "up",
}


def _is_supported_normal_key(key: str) -> bool:
    normalized = key.strip().casefold()
    return bool(
        normalized in _NAMED_NORMAL_KEYS
        or re.fullmatch(r"[a-z0-9]", normalized)
        or re.fullmatch(r"f(?:[1-9]|1[0-2])", normalized)
    )
