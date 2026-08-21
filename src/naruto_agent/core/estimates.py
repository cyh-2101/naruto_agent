from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class UnavailableReason(StrEnum):
    """Why a screen-derived value is unavailable instead of merely false or zero."""

    NOT_IMPLEMENTED = "not_implemented"
    NOT_OBSERVED = "not_observed"
    OCCLUDED = "occluded"
    LOW_CONFIDENCE = "low_confidence"
    INVALID = "invalid"
    OUT_OF_FRAME = "out_of_frame"
    UNSUPPORTED = "unsupported"


class EstimateStatus(StrEnum):
    VALID = "valid"
    UNKNOWN = "unknown"
    INVALID = "invalid"
    STALE = "stale"
    NOT_IMPLEMENTED = "not_implemented"


@dataclass(frozen=True, slots=True)
class Estimate(Generic[T]):
    """A value plus screen-only evidence, lifetime, and explicit unavailability state."""

    value: T | None
    confidence: float
    observed_at_ns: int
    valid_until_ns: int
    source: str
    provenance: str
    source_version: str | None = None
    unavailable_reason: UnavailableReason | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
        if self.observed_at_ns <= 0:
            raise ValueError("observed_at_ns must be positive")
        if self.valid_until_ns < self.observed_at_ns:
            raise ValueError("valid_until_ns cannot precede observed_at_ns")
        if not self.source.strip() or not self.provenance.strip():
            raise ValueError("source and provenance cannot be empty")
        if self.value is None and self.unavailable_reason is None:
            raise ValueError("an unavailable estimate requires unavailable_reason")
        if self.value is not None and self.unavailable_reason is not None:
            raise ValueError("an available estimate cannot have unavailable_reason")

    @classmethod
    def known(
        cls,
        value: T,
        *,
        confidence: float,
        observed_at_ns: int,
        valid_until_ns: int,
        source: str,
        provenance: str,
        source_version: str | None = None,
    ) -> Estimate[T]:
        return cls(
            value=value,
            confidence=confidence,
            observed_at_ns=observed_at_ns,
            valid_until_ns=valid_until_ns,
            source=source,
            provenance=provenance,
            source_version=source_version,
        )

    @classmethod
    def unavailable(
        cls,
        reason: UnavailableReason,
        *,
        observed_at_ns: int,
        valid_until_ns: int,
        source: str,
        provenance: str,
        source_version: str | None = None,
        confidence: float = 0.0,
    ) -> Estimate[T]:
        return cls(
            value=None,
            confidence=confidence,
            observed_at_ns=observed_at_ns,
            valid_until_ns=valid_until_ns,
            source=source,
            provenance=provenance,
            source_version=source_version,
            unavailable_reason=reason,
        )

    def is_fresh_at(self, timestamp_ns: int) -> bool:
        if timestamp_ns <= 0:
            raise ValueError("timestamp_ns must be positive")
        return self.observed_at_ns <= timestamp_ns <= self.valid_until_ns

    def is_usable_at(self, timestamp_ns: int, *, min_confidence: float = 0.0) -> bool:
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be in [0, 1]")
        return (
            self.value is not None
            and self.confidence >= min_confidence
            and self.is_fresh_at(timestamp_ns)
        )

    def status_at(self, timestamp_ns: int) -> EstimateStatus:
        if timestamp_ns < self.observed_at_ns:
            return EstimateStatus.INVALID
        if timestamp_ns > self.valid_until_ns:
            return EstimateStatus.STALE
        if self.unavailable_reason is UnavailableReason.NOT_IMPLEMENTED:
            return EstimateStatus.NOT_IMPLEMENTED
        if self.unavailable_reason is UnavailableReason.INVALID:
            return EstimateStatus.INVALID
        if self.value is None:
            return EstimateStatus.UNKNOWN
        return EstimateStatus.VALID

    def to_record(self, *, at_ns: int) -> dict[str, Any]:
        """Serialize evidence for datasets; policy views use a provenance-free projection."""

        value = self.value
        if isinstance(value, StrEnum):
            value = value.value
        elif hasattr(value, "x") and hasattr(value, "y"):
            value = {"x": value.x, "y": value.y}
        return {
            "value": value,
            "confidence": self.confidence,
            "observed_at_ns": self.observed_at_ns,
            "valid_until_ns": self.valid_until_ns,
            "source": self.source,
            "provenance": self.provenance,
            "source_version": self.source_version,
            "unavailable_reason": (
                self.unavailable_reason.value if self.unavailable_reason is not None else None
            ),
            "status": self.status_at(at_ns).value,
        }
