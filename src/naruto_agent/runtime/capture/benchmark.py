from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import psutil

from naruto_agent.core.interfaces import CaptureBackend
from naruto_agent.runtime.capture.common import CaptureBenchmark
from naruto_agent.runtime.clock import monotonic_ns


def run_capture_benchmark(
    backend: CaptureBackend,
    *,
    frame_limit: int,
    sample_path: Path | None = None,
) -> CaptureBenchmark:
    if frame_limit < 1:
        raise ValueError("frame_limit must be positive")
    process = psutil.Process()
    memory_before = process.memory_info().rss
    latencies: list[float] = []
    duplicates = 0
    dropped = 0
    last_image = None
    started = time.perf_counter()
    backend.start()
    try:
        for frame in backend.frames():
            latencies.append(max(0.0, (monotonic_ns() - frame.timestamp_ns) / 1_000_000))
            duplicates += int(frame.duplicate)
            dropped += frame.dropped_before
            last_image = frame.image
            if len(latencies) >= frame_limit:
                break
    finally:
        backend.stop()
    duration = max(time.perf_counter() - started, 1e-9)
    memory_after = process.memory_info().rss
    if sample_path is not None:
        if last_image is None:
            raise RuntimeError("capture produced no sample frame")
        _export_sample(last_image, sample_path)
    values = np.asarray(latencies, dtype=np.float64)
    return CaptureBenchmark(
        frames=len(latencies),
        duration_seconds=duration,
        fps=len(latencies) / duration,
        latency_ms_p50=float(np.percentile(values, 50)) if len(values) else 0.0,
        latency_ms_p95=float(np.percentile(values, 95)) if len(values) else 0.0,
        latency_ms_p99=float(np.percentile(values, 99)) if len(values) else 0.0,
        duplicates=duplicates,
        dropped_frames=dropped,
        memory_growth_mib=(memory_after - memory_before) / (1024 * 1024),
    )


def _export_sample(image: np.ndarray, path: Path) -> None:
    if path.suffix.lower() != ".npy":
        raise ValueError("Foundation sample export supports explicit .npy output only")
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, image, allow_pickle=False)
