from __future__ import annotations

import hashlib
import queue
import threading
from dataclasses import dataclass, replace

import numpy as np

from naruto_agent.core.contracts import FramePacket, ImageArray


class DuplicateFrameDetector:
    """Detect exact consecutive duplicates and sustained frozen capture."""

    def __init__(self, frozen_frame_threshold: int = 6) -> None:
        if frozen_frame_threshold < 1:
            raise ValueError("frozen_frame_threshold must be positive")
        self._threshold = frozen_frame_threshold
        self._previous_digest: bytes | None = None
        self._consecutive_duplicates = 0

    @property
    def consecutive_duplicates(self) -> int:
        return self._consecutive_duplicates

    @property
    def frozen(self) -> bool:
        return self._consecutive_duplicates >= self._threshold

    def inspect(self, image: ImageArray) -> bool:
        contiguous = np.ascontiguousarray(image)
        digest = hashlib.blake2b(memoryview(contiguous), digest_size=16).digest()
        duplicate = digest == self._previous_digest
        self._consecutive_duplicates = self._consecutive_duplicates + 1 if duplicate else 0
        self._previous_digest = digest
        return duplicate


class BoundedFrameQueue:
    """Drop the oldest frame under pressure; never grow without a bound."""

    def __init__(self, maxsize: int) -> None:
        if maxsize < 1:
            raise ValueError("maxsize must be positive")
        self._queue: queue.Queue[FramePacket] = queue.Queue(maxsize=maxsize)
        self._lock = threading.Lock()
        self.total_dropped = 0

    @property
    def maxsize(self) -> int:
        return self._queue.maxsize

    def put(self, frame: FramePacket) -> int:
        dropped = 0
        with self._lock:
            if self._queue.full():
                try:
                    self._queue.get_nowait()
                    dropped = 1
                    self.total_dropped += 1
                except queue.Empty:
                    pass
            if dropped and frame.dropped_before == 0:
                frame = replace(frame, dropped_before=dropped)
            self._queue.put_nowait(frame)
        return dropped

    def get(self, timeout: float | None = None) -> FramePacket:
        return self._queue.get(timeout=timeout)

    def empty(self) -> bool:
        return self._queue.empty()

    def qsize(self) -> int:
        return self._queue.qsize()


@dataclass(frozen=True, slots=True)
class CaptureBenchmark:
    frames: int
    duration_seconds: float
    fps: float
    latency_ms_p50: float
    latency_ms_p95: float
    latency_ms_p99: float
    duplicates: int
    dropped_frames: int
    memory_growth_mib: float

    def as_dict(self) -> dict[str, float | int]:
        return {
            "frames": self.frames,
            "duration_seconds": self.duration_seconds,
            "fps": self.fps,
            "latency_ms_p50": self.latency_ms_p50,
            "latency_ms_p95": self.latency_ms_p95,
            "latency_ms_p99": self.latency_ms_p99,
            "duplicates": self.duplicates,
            "dropped_frames": self.dropped_frames,
            "memory_growth_mib": self.memory_growth_mib,
        }
