from __future__ import annotations

from collections.abc import Iterator

import numpy as np

from naruto_agent.core.contracts import FramePacket
from naruto_agent.runtime.clock import monotonic_ns


class MockCaptureBackend:
    """Deterministic safe backend for unit tests and architecture integration."""

    def __init__(
        self,
        *,
        frame_count: int = 10,
        width: int = 320,
        height: int = 180,
        source_id: str = "mock",
        duplicate_every: int | None = None,
    ) -> None:
        if frame_count < 0:
            raise ValueError("frame_count must be non-negative")
        self._frame_count = frame_count
        self._width = width
        self._height = height
        self._source_id = source_id
        self._duplicate_every = duplicate_every
        self._running = False

    @property
    def source_id(self) -> str:
        return self._source_id

    def start(self) -> None:
        self._running = True

    def frames(self) -> Iterator[FramePacket]:
        if not self._running:
            raise RuntimeError("capture backend must be started before reading frames")
        last_timestamp = 0
        previous: np.ndarray | None = None
        for frame_id in range(self._frame_count):
            timestamp = monotonic_ns()
            if timestamp <= last_timestamp:
                timestamp = last_timestamp + 1
            last_timestamp = timestamp

            duplicate = (
                self._duplicate_every is not None
                and frame_id > 0
                and frame_id % self._duplicate_every == 0
                and previous is not None
            )
            if duplicate:
                image = previous.copy()
            else:
                image = np.full(
                    (self._height, self._width, 3),
                    fill_value=frame_id % 256,
                    dtype=np.uint8,
                )
            previous = image
            yield FramePacket(
                frame_id=frame_id,
                timestamp_ns=timestamp,
                source_id=self._source_id,
                image=image,
                duplicate=duplicate,
            )

    def stop(self) -> None:
        self._running = False
