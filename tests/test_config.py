from pathlib import Path

import pytest
from pydantic import ValidationError

from naruto_agent.config.loader import load_base_config, load_emulator_profile
from naruto_agent.config.models import EmulatorProfile

ROOT = Path(__file__).parents[1]


def test_base_and_example_profile_validate_with_safe_defaults() -> None:
    base = load_base_config(ROOT / "configs" / "base.yaml")
    profile = load_emulator_profile(ROOT / "configs" / "emulator.example.yaml")
    assert base.runtime.dry_run
    assert not base.runtime.live_input_enabled
    assert not profile.verified
    with pytest.raises(ValueError, match="not verified"):
        profile.assert_live_ready()


def test_verified_profile_rejects_missing_control_bindings() -> None:
    data = load_emulator_profile(ROOT / "configs" / "emulator.example.yaml").model_dump()
    data["verified"] = True
    data["window"]["title_contains"] = "Emulator"
    with pytest.raises(ValidationError, match="all live controls"):
        EmulatorProfile.model_validate(data)


def test_invalid_normalized_ui_region_is_rejected() -> None:
    data = load_emulator_profile(ROOT / "configs" / "emulator.example.yaml").model_dump()
    data["ui_regions"]["self_health"] = (0.1, 0.1, 1.1, 0.2)
    with pytest.raises(ValidationError, match="normalized"):
        EmulatorProfile.model_validate(data)


def test_invalid_normal_key_binding_is_rejected_before_live_preflight() -> None:
    data = load_emulator_profile(ROOT / "configs" / "emulator.example.yaml").model_dump()
    data["controls"]["emergency_stop"] = "not-a-key"
    with pytest.raises(ValidationError, match="normal-key"):
        EmulatorProfile.model_validate(data)
