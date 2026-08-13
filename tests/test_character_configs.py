from pathlib import Path

from naruto_agent.core.enums import CharacterId
from naruto_agent.skills.spec import CharacterRegistry


def test_all_three_character_configs_validate() -> None:
    root = Path(__file__).parents[1] / "configs" / "characters"
    registry = CharacterRegistry.from_directory(root)
    assert set(registry.ids()) == {
        CharacterId.TAKA_SASUKE,
        CharacterId.WHITE_MASK,
        CharacterId.PAIN,
    }


def test_character_mechanics_remain_unverified() -> None:
    root = Path(__file__).parents[1] / "configs" / "characters"
    registry = CharacterRegistry.from_directory(root)
    for character_id in registry.ids():
        config = registry.get(character_id)
        assert not config.verified
        assert config.status == "declared"
        assert all(not skill.verified for skill in config.skills.values())
