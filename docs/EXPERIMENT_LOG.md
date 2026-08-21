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

## EXP-20260821-001 — Architecture V2 contract refactor

- Goal: translate approved screen-only architecture ideas into durable runtime/data contracts,
  tests, documentation, and a passive proposed Work Order 002 without starting learning or input.
- Baseline commit: `95891fd` on `main`.
- Branch: `architecture/v2-screen-only-policy`.
- Environment: Windows PowerShell, Python 3.12.13 virtual environment; no emulator interaction.
- Research inputs:
  - repository architecture/status/safety documentation;
  - user-provided `docs/SHUKAI_KIHAN_ARCHITECTURE_IDEAS.md`;
  - local 21-page `D:\projects\kihan\arxiv-2406.01103.pdf` text layer, with relevant identity,
    factorized-action, mask, HELT/PFSP, and behavior sections located.
- Commands:
  - `git switch -c architecture/v2-screen-only-policy`;
  - `.\.venv\Scripts\python.exe -m pytest -ra`;
  - `.\.venv\Scripts\python.exe -m ruff check .` and `ruff format src tests`;
  - `.\.venv\Scripts\python.exe -m compileall -q src tests`;
  - two attempts at `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"`;
  - successful `.\.venv\Scripts\python.exe -m pip install -e .`.
- Results:
  - initial compilation and Ruff baseline passed;
  - initial pytest collection failed because the existing virtual environment lacked the editable
    project and Pydantic;
  - after core dependency restoration, the first V2 checkpoint passed 60 tests;
  - after typed V2 action/capability/dispatch records, the suite passed `61 passed in 0.66s`;
  - final gap tests for optional strategic intent, capability expiry, and scene-entity serialization
    produced `64 passed in 0.68s`;
  - final pre-commit rerun produced `64 passed in 0.73s`, Ruff passed, compilation passed, and
    `git diff --check` reported no whitespace errors;
  - Ruff and bytecode compilation passed after the code changes;
  - the original 40 Foundation tests remain in the passing suite;
  - no test constructed a native Windows input backend or used a live marker.
  - native doctor completed with zero visible emulator candidates and did not capture or send input;
  - mock episode `b1bb1f5f-40bb-4a66-bc21-19a26b6f3d40` finalized with 8 frames, 0 input
    events, 8 neutral control intervals, expected `raw_frame_fallback`, and 0 validation errors.
- Verified contracts:
  - estimate value/unknown/confidence/freshness behavior;
  - canonical temporal state and scene-entity schemas;
  - IR/SQ/IQ identity visibility and serialized leak protection;
  - nine-way factorized movement;
  - capability rejection before adaptation and SafetyGate rejection after acceptance;
  - V2 episode/runtime serialization and V1 manifest readability.
- Failures or anomalies:
  - the PDF render wrapper referenced a missing Poppler executable path; selected-page PNG rendering
    failed, while text extraction succeeded;
  - both dev-extra installs stalled while downloading the 11.2 MB mypy wheel; the second process was
    terminated after repeated no-progress intervals;
  - mypy was therefore unavailable and not run;
  - the failed pre-install pytest collection is not counted as a code test result.
- Artifacts:
  - source, tests, ADR, documentation, and proposed Work Order 002 only;
  - no dataset, capture, calibration, video, game asset, model, checkpoint, or credential generated.
- Interpretation:
  - Architecture V2 contracts and their mock/synthetic safety boundaries are verified;
  - passive game perception, native capture, character mechanics, trained policy quality, and live
    gameplay remain unverified or absent;
  - Shūkai/Kihan provide research ideas only; their hidden-state, PPO, league, direct-input, and
    reward results are not project evidence.
- Next action: Product Owner review of the passive-only Work Order 002; do not start it or any
  learning/input work without explicit authorization.

## EXP-20260822-001 — Remove IQ and adopt IR-primary/SQ-fallback views

- Goal: remove the identity-free IQ view and align the current architecture with the Product Owner's
  maximum-performance objective while retaining a robust identity-unavailable path.
- Baseline commit: `0e9e940` on branch `architecture/v2-screen-only-policy`.
- Environment: Windows PowerShell, Python 3.12.13 virtual environment; no emulator interaction.
- Commands:
  - `rg` inventory of IQ/`identity_quiet` references across source, tests, and documentation;
  - `.\.venv\Scripts\python.exe -m pytest -ra`;
  - `.\.venv\Scripts\python.exe -m ruff check .`;
  - `.\.venv\Scripts\python.exe -m compileall -q src tests scripts`;
  - `.\.venv\Scripts\python.exe -m mypy src\naruto_agent`;
  - `.\.venv\Scripts\python.exe -m mypy --python-version 3.12
    src\naruto_agent\core\observations.py`;
  - `git diff --check` and scoped status/diff audits.
- Results:
  - removed `ObservationViewType.IDENTITY_QUIET` and the builder IQ branch;
  - current enum and tests support only IR and SQ;
  - IR is documented as primary when opponent identity is fresh/confident;
  - SQ is documented as fallback for unknown, stale, low-confidence, or conflicting identity and as
    a future identity-dropout training view;
  - safe suite: `64 passed in 1.10s`;
  - Ruff and bytecode compilation passed;
  - targeted Python 3.12 mypy for the changed observation module passed;
  - `git diff --check` passed.
- Failures or anomalies:
  - automatic IR-to-SQ selection remains intentionally unimplemented because no passive identity
    estimator has measured confidence/freshness calibration;
  - full-package mypy failed with five pre-analysis dependency/target errors: missing `types-psutil`,
    missing optional `torch`, and NumPy 2.5.2 stub syntax incompatible with the configured Python
    3.11 target. No ignore rule or weakened configuration was added;
  - pre-existing untracked `docs.zip` was present at session start and was preserved, not inspected,
    modified, deleted, or staged.
- Artifacts: source/test/documentation changes and ADR-016 only; no data, capture, calibration,
  model, checkpoint, credential, or input artifact.
- Interpretation: removing reliable identity cannot improve the theoretical information ceiling;
  robustness will use SQ fallback, identity dropout, and missing/corrupted-identity evaluation.
- Next action: after explicit Work Order 002 authorization, measure passive identity quality and
  implement a reason-recording IR/SQ resolver. Do not train or send generated input.

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
