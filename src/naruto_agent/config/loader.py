from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from naruto_agent.config.models import BaseConfig, CharacterConfig, EmulatorProfile


def load_yaml(path: str | Path) -> dict[str, Any]:
    resolved = Path(path)
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    with resolved.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected a YAML mapping in {resolved}")
    return data


def load_character_config(path: str | Path) -> CharacterConfig:
    return CharacterConfig.model_validate(load_yaml(path))


def load_emulator_profile(path: str | Path) -> EmulatorProfile:
    return EmulatorProfile.model_validate(load_yaml(path))


def load_base_config(path: str | Path) -> BaseConfig:
    return BaseConfig.model_validate(load_yaml(path))
