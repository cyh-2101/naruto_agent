from __future__ import annotations

import time


def monotonic_ns() -> int:
    """High-resolution monotonic runtime timestamp in nanoseconds."""

    return time.perf_counter_ns()
