import time

import numpy as np

from naruto_agent.core.contracts import FramePacket
from naruto_agent.runtime.capture.common import BoundedFrameQueue, DuplicateFrameDetector


def _frame(frame_id: int) -> FramePacket:
    return FramePacket(
        frame_id=frame_id,
        timestamp_ns=time.monotonic_ns() + frame_id,
        source_id="test",
        image=np.full((2, 2, 3), frame_id, dtype=np.uint8),
    )


def test_bounded_queue_drops_oldest_without_growth() -> None:
    frames = BoundedFrameQueue(maxsize=2)
    frames.put(_frame(0))
    frames.put(_frame(1))
    assert frames.put(_frame(2)) == 1
    assert frames.qsize() == 2
    assert frames.total_dropped == 1
    assert frames.get().frame_id == 1
    newest = frames.get()
    assert newest.frame_id == 2
    assert newest.dropped_before == 1


def test_duplicate_and_frozen_frame_detection() -> None:
    detector = DuplicateFrameDetector(frozen_frame_threshold=2)
    first = np.zeros((2, 2, 3), dtype=np.uint8)
    assert not detector.inspect(first)
    assert detector.inspect(first.copy())
    assert not detector.frozen
    assert detector.inspect(first.copy())
    assert detector.frozen
    assert not detector.inspect(np.ones_like(first))
    assert not detector.frozen
