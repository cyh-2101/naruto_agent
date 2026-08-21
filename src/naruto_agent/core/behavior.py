from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BehaviorProfile:
    """Optional style targets. Unset values remain unknown and never become mechanics."""

    profile_id: str
    version: str
    aggression: float | None = None
    caution: float | None = None
    resource_conservation: float | None = None
    substitution_preference: float | None = None
    special_move_preference: float | None = None
    preferred_distance: str | None = None
    verified: bool = False
    evidence_reference: str | None = None

    def __post_init__(self) -> None:
        if not self.profile_id.strip() or not self.version.strip():
            raise ValueError("behavior profile id and version cannot be empty")
        for name in (
            "aggression",
            "caution",
            "resource_conservation",
            "substitution_preference",
            "special_move_preference",
        ):
            value = getattr(self, name)
            if value is not None and not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")
        if self.verified and not self.evidence_reference:
            raise ValueError("verified behavior profiles require evidence_reference")
