from __future__ import annotations

import importlib
import queue
import sys
import threading
import time
from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np

from naruto_agent.core.contracts import FramePacket
from naruto_agent.runtime.capture.common import BoundedFrameQueue, DuplicateFrameDetector
from naruto_agent.runtime.clock import monotonic_ns
from naruto_agent.runtime.window import WindowInfo


@dataclass(frozen=True, slots=True)
class WindowCaptureProfile:
    window: WindowInfo
    crop_pixels: tuple[int, int, int, int] | None
    target_fps: int = 30
    queue_size: int = 8
    frozen_frame_threshold: int = 6

    def __post_init__(self) -> None:
        if self.target_fps < 1 or self.queue_size < 1 or self.frozen_frame_threshold < 1:
            raise ValueError("capture rate, queue size, and frozen threshold must be positive")
        if self.crop_pixels is not None:
            left, top, right, bottom = self.crop_pixels
            if min(left, top) < 0 or right <= left or bottom <= top:
                raise ValueError("invalid capture crop")
            if right > self.window.width or bottom > self.window.height:
                raise ValueError("capture crop exceeds the selected window")

    @property
    def desktop_region(self) -> tuple[int, int, int, int]:
        if self.crop_pixels is None:
            return (
                self.window.left,
                self.window.top,
                self.window.left + self.window.width,
                self.window.top + self.window.height,
            )
        left, top, right, bottom = self.crop_pixels
        return (
            self.window.left + left,
            self.window.top + top,
            self.window.left + right,
            self.window.top + bottom,
        )


class DXCamCaptureBackend:
    """Bounded native-Windows Desktop Duplication capture using optional DXCam."""

    def __init__(self, profile: WindowCaptureProfile, source_id: str = "dxcam") -> None:
        if sys.platform != "win32":
            raise RuntimeError("DXCam capture requires native Windows")
        if importlib.util.find_spec("dxcam") is None:
            raise RuntimeError("DXCam is not installed; install the project windows extra")
        self._profile = profile
        self._source_id = source_id
        self._frames = BoundedFrameQueue(profile.queue_size)
        self._detector = DuplicateFrameDetector(profile.frozen_frame_threshold)
        self._running = threading.Event()
        self._thread: threading.Thread | None = None
        self._camera: object | None = None
        self._producer_error: BaseException | None = None

    @property
    def source_id(self) -> str:
        return self._source_id

    @property
    def dropped_frames(self) -> int:
        return self._frames.total_dropped

    @property
    def frozen(self) -> bool:
        return self._detector.frozen

    def start(self) -> None:
        if self._running.is_set():
            raise RuntimeError("capture backend is already running")
        dxcam = importlib.import_module("dxcam")
        self._camera = dxcam.create(output_color="BGR")
        self._running.set()
        self._producer_error = None
        self._thread = threading.Thread(target=self._produce, name="dxcam-capture", daemon=True)
        self._thread.start()

    def _produce(self) -> None:
        assert self._camera is not None
        camera = self._camera
        frame_id = 0
        period = 1.0 / self._profile.target_fps
        last_timestamp = 0
        try:
            while self._running.is_set():
                cycle_started = time.perf_counter()
                image = camera.grab(region=self._profile.desktop_region)
                if image is not None:
                    array = np.asarray(image, dtype=np.uint8)
                    timestamp = max(monotonic_ns(), last_timestamp + 1)
                    last_timestamp = timestamp
                    packet = FramePacket(
                        frame_id=frame_id,
                        timestamp_ns=timestamp,
                        source_id=self._source_id,
                        image=array,
                        duplicate=self._detector.inspect(array),
                    )
                    self._frames.put(packet)
                    frame_id += 1
                remaining = period - (time.perf_counter() - cycle_started)
                if remaining > 0:
                    time.sleep(remaining)
        except BaseException as exc:
            self._producer_error = exc
            self._running.clear()

    def frames(self) -> Iterator[FramePacket]:
        if not self._running.is_set():
            raise RuntimeError("capture backend must be started before reading frames")
        while self._running.is_set() or not self._frames.empty():
            try:
                yield self._frames.get(timeout=0.25)
            except queue.Empty:
                if self._producer_error is not None:
                    raise RuntimeError("DXCam producer failed") from self._producer_error
        if self._producer_error is not None:
            raise RuntimeError("DXCam producer failed") from self._producer_error

    def stop(self) -> None:
        self._running.clear()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        if self._camera is not None:
            stop = getattr(self._camera, "stop", None)
            if callable(stop):
                stop()
        self._thread = None
        self._camera = None
