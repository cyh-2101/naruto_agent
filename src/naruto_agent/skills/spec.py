from __future__ import annotations

from pathlib import Path

from naruto_agent.config.loader import load_character_config
from naruto_agent.config.models import CharacterConfig
from naruto_agent.core.enums import CharacterId


class CharacterRegistry:
    def __init__(self, configs: dict[CharacterId, CharacterConfig]) -> None:
        self._configs = dict(configs)

    @classmethod
    def from_directory(cls, directory: str | Path) -> CharacterRegistry:
        root = Path(directory)
        configs: dict[CharacterId, CharacterConfig] = {}
        for path in sorted(root.glob("*.yaml")):
            config = load_character_config(path)
            if config.character_id in configs:
                raise ValueError(f"duplicate character ID: {config.character_id}")
            configs[config.character_id] = config
        return cls(configs)

    def get(self, character_id: CharacterId) -> CharacterConfig:
        try:
            return self._configs[character_id]
        except KeyError as exc:
            raise KeyError(f"character is not registered: {character_id}") from exc

    def ids(self) -> tuple[CharacterId, ...]:
        return tuple(self._configs)
