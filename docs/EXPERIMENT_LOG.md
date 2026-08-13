# Experiment Log

Append entries. Do not delete failed runs.

## Starter package validation

- Date: generated with the starter package
- Environment: container-based validation, not the user's native Windows runtime
- Commands:
  - `PYTHONPATH=src pytest -q`
- Result: 13 starter tests passed; Python bytecode compilation passed.
- Limitations:
  - no real emulator;
  - no Windows capture/input verification;
  - no game data or character mechanics;
  - Ruff and mypy were not available in the package-generation environment and were not run.

## EXP-20260813-001 — Work Order 001 baseline and environment preparation

- Goal: establish the actual local runtime and preserve baseline failures before implementation.
- Code commit: unavailable; `git status`, `git branch`, and `git log` all reported that
  `D:\projects\naruto_agent` was not a Git repository.
- Environment:
  - native Windows;
  - shell default `python`: 3.14.5 at `C:\msys64\ucrt64\bin\python.exe`;
  - compatible bundled interpreter used to create `.venv`: Python 3.12.13.
- Configuration: no emulator or character calibration loaded.
- Dataset/model version: none.
- Commands:
  - `python --version`
  - `python -m pytest`
  - `python -m ruff check .`
  - `python -m mypy src/naruto_agent`
  - `python scripts/doctor.py --project-root .`
  - `<bundled-python-3.12> -m venv .venv`
  - `.\.venv\Scripts\python.exe -m pip install -e ".[dev,windows]"`
- Results:
  - default Python was outside the supported 3.11/3.12 range;
  - pytest, Ruff, and mypy were not installed in the default interpreter;
  - the starter doctor could not import the uninstalled package;
  - the Python 3.12 virtual environment was created successfully.
- Artifacts: ignored `.venv/` only.
- Failures or anomalies:
  - two editable-install attempts timed out after approximately 120 and 300 seconds without package
    output;
  - later broad and direct-wheel attempts also timed out;
  - narrow one-package installs succeeded for pytest, PyYAML, psutil, and Typer/Rich;
  - repeated Ruff downloads timed out, including a six-minute retry, but inspection showed that the
    Ruff wheel had installed before that timeout;
  - a later six-minute mypy/types-PyYAML install timed out and left mypy unavailable.
- Interpretation: implementation and tests must use the compatible Python 3.12 environment. Network
  package-download behavior is unreliable and must not be mistaken for a source-code failure.
- Next action: implement the Foundation slice, run all available safe tests, and record static-check
  limitations explicitly.

## EXP-20260813-002 — Work Order 001 safe verification

- Goal: verify configuration, contracts, safety behavior, recording, native diagnostics, and the mock
  vertical loop without an emulator or real input.
- Code commit: unavailable; the directory was still not a Git worktree.
- Environment:
  - native Windows 11 build 26200;
  - Python 3.12.13, 64-bit;
  - 32 logical CPU cores;
  - 15.22 GiB RAM;
  - NVIDIA GeForce RTX 5070 Ti Laptop GPU, driver 573.22, 12227 MiB reported by `nvidia-smi`;
  - high-resolution monotonic source: `QueryPerformanceCounter`, reported resolution 100 ns;
  - DXCam, pywin32, pynput, OpenCV, and PyTorch not installed;
  - no visible top-level emulator candidate of at least 640x360.
- Configuration:
  - `configs/base.yaml` safe defaults;
  - `configs/emulator.example.yaml` remains unverified;
  - all three character configs remain declared and unverified.
- Dataset/model version: none. No model was created or loaded.
- Commands:
  - `$env:PYTHONPATH='src;<bundled-python-site-packages>'; .\.venv\Scripts\python.exe -m pytest -ra`
  - `.\.venv\Scripts\python.exe -m compileall -f -q src tests scripts`
  - `.\.venv\Scripts\python.exe scripts\doctor.py --project-root . --json`
  - `.\.venv\Scripts\python.exe scripts\runtime.py calibrate-validate configs\emulator.example.yaml`
  - `.\.venv\Scripts\python.exe scripts\runtime.py mock-demo --output-root <temporary> --frames 8`
  - `.\.venv\Scripts\python.exe scripts\episode.py validate <temporary-episode>`
  - `.\.venv\Scripts\python.exe scripts\episode.py inspect <temporary-episode>`
  - safe mock call to `run_capture_benchmark(MockCaptureBackend(...), frame_limit=100)`
- Results:
  - final combined rerun: `40 passed in 0.99s`;
  - Ruff reported `All checks passed!` after its first run identified 21 formatting/lint findings and
    the findings were fixed;
  - bytecode compilation completed with exit code 0;
  - doctor completed with exit code 0 and all three local paths writable;
  - the example profile passed schema validation and remained `verified: false`;
  - final mock episode `b3b75646-09fc-46e1-9a43-b0fd4ec3e08c` finalized with 8 frames, 0 raw
    input events, 8 neutral control intervals, expected `raw_frame_fallback`, and 0 validation errors;
  - mock benchmark metric plumbing processed 100 synthetic frames, detected 9 intentional
    duplicates, reported 0 drops, p50/p95/p99 consumer latency of 0.0032/0.0056/0.04125 ms,
    approximately 0.324 MiB resident-memory change, and a 0.000495-second measured duration.
- Artifacts:
  - final temporary episode under
    `C:\Users\chiyu\AppData\Local\Temp\naruto-agent-final-56e1f123910740aba0b5749968a84d51\b3b75646-09fc-46e1-9a43-b0fd4ec3e08c`;
  - no repository capture or dataset artifact was generated.
- Failures or anomalies:
  - mypy could not be installed and therefore was not run;
  - Git commit/status provenance could not be collected because the directory was not a Git worktree;
  - the mock benchmark's synthetic throughput is intentionally not interpreted as native capture
    performance.
- Interpretation:
  - mock contracts, default dry-run behavior, fail-safe transitions, bounded queue behavior, timestamp
    checks, exception finalization, validation, and non-Windows graceful behavior are verified;
  - no claim is made about DXCam performance, real crop correctness, `SendInput`, a physical
    emergency-stop hotkey, emulator focus loss, or character mechanics.
- Next action: establish Git provenance, install the Windows extra, open only a training-mode emulator,
  create an unverified local profile, and benchmark native capture with input disabled.

## Entry template

### EXP-YYYYMMDD-NNN — Title

- Goal:
- Code commit:
- Environment:
- Configuration:
- Dataset/model version:
- Commands:
- Results:
- Artifacts:
- Failures or anomalies:
- Interpretation:
- Next action:
