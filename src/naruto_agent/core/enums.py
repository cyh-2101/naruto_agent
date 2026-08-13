from enum import StrEnum


class CharacterId(StrEnum):
    TAKA_SASUKE = "taka_sasuke"
    WHITE_MASK = "white_mask"
    PAIN = "pain"
    UNKNOWN = "unknown"


class MovementDirection(StrEnum):
    NEUTRAL = "neutral"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    UP_LEFT = "up_left"
    UP_RIGHT = "up_right"
    DOWN_LEFT = "down_left"
    DOWN_RIGHT = "down_right"


class ButtonAction(StrEnum):
    NONE = "none"
    NORMAL_ATTACK = "normal_attack"
    SKILL_1 = "skill_1"
    SKILL_2 = "skill_2"
    ULTIMATE = "ultimate"
    SUBSTITUTION = "substitution"
    SECRET_SCROLL = "secret_scroll"
    SUMMON = "summon"


class RoundPhase(StrEnum):
    UNKNOWN = "unknown"
    PRE_ROUND = "pre_round"
    ACTIVE = "active"
    ROUND_END = "round_end"
    MATCH_END = "match_end"


class AnimationState(StrEnum):
    UNKNOWN = "unknown"
    IDLE = "idle"
    MOVING = "moving"
    ATTACKING = "attacking"
    HIT = "hit"
    KNOCKED_DOWN = "knocked_down"
    RECOVERING = "recovering"


class StrategicIntent(StrEnum):
    NEUTRAL = "neutral"
    PRESSURE = "pressure"
    BAIT_SKILL = "bait_skill"
    BAIT_SUBSTITUTION = "bait_substitution"
    DEFEND = "defend"
    RETREAT = "retreat"
    WAIT_COOLDOWN = "wait_cooldown"
    PUNISH = "punish"
    ESCAPE = "escape"
    FINISH_COMBO = "finish_combo"
    SAVE_RESOURCES = "save_resources"
