# Architecture V2 Runbook

All commands in this runbook are dry-run or read-only unless a section explicitly says otherwise.
There is no live gameplay runner. Work Order 002 is proposed but not authorized and permits only
passive capture/recording if later approved.

## 1. Create a supported environment

Use 64-bit Python 3.11 or 3.12 on Windows PowerShell:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

If the default `python` is not 3.11/3.12, use its full path or the bootstrap parameter:

```powershell
.\scripts\bootstrap.ps1 -PythonExecutable "C:\Path\To\Python312\python.exe"
```

Native capture and emergency-stop dependencies are optional and installed separately:

```powershell
python -m pip install -e ".[dev,windows]"
```

Do not install `ml` extras for the current architecture checkpoint or proposed Work Order 002. No
approved learning or inference component uses them.

## 2. Run every safe check

```powershell
python scripts/doctor.py --project-root .
python -m pytest -ra
python -m ruff check .
python -m mypy src/naruto_agent
python -m compileall -q src tests scripts
```

The test suite uses only synthetic frames, mock/dry-run input, temporary episodes, and temporary
configuration paths. It contains a guard test that rejects a live marker or native input backend
construction in the default suite.

At the 2026-08-21 Architecture V2 checkpoint, the expected safe result is 64 passing tests. Treat a
different count as something to inspect, not a reason to weaken collection or assertions. If mypy is
unavailable, record that limitation separately.

## 3. Exercise the mock vertical loop

```powershell
python scripts/runtime.py mock-demo --frames 8
```

The command prints a temporary episode directory. It runs:

```text
mock capture
  -> explicitly unknown placeholder observation
  -> zero-confidence neutral policy output
  -> safety gate and action scheduler
  -> mock input
  -> bounded raw-frame recorder
```

Inspect and validate the printed path:

```powershell
python scripts/episode.py inspect "<episode-directory>"
python scripts/episode.py validate "<episode-directory>"
```

The default mock episode contains no raw key events because the policy output is neutral. Its full
control-state intervals are still recorded.

## 4. Diagnose native Windows without capture or input

```powershell
python scripts/doctor.py --project-root . --json
python scripts/runtime.py windows --minimum-width 640 --minimum-height 360
```

The doctor may enumerate visible top-level window metadata, but it does not capture pixels or send
input. Close unrelated windows before calibration to reduce privacy risk.

Running native capture against an emulator belongs to an explicitly authorized Work Order 002. The
diagnostic commands alone do not start that work order.

If no candidate appears:

- confirm the command runs in native Windows rather than WSL;
- open the emulator in training mode;
- rerun the doctor;
- do not weaken visibility or size checks merely to force a match.

## 5. Create an unverified local calibration

Do this for a real emulator only after Work Order 002 authorization. Profile creation itself sends no
input.

Profiles are machine-specific and must remain under ignored `configs/local/`. The command refuses to
overwrite an existing file or any example path.

```powershell
python scripts/runtime.py calibrate-create local_training `
  --output configs/local/local_training.yaml `
  --title "<unique emulator title substring>" `
  --process "<emulator executable name>"
```

Optional repeatable fields are available from command help:

```powershell
python scripts/runtime.py calibrate-create --help
```

- `--crop L,T,R,B` uses window-relative pixels;
- `--ui-region NAME=L,T,R,B` uses normalized coordinates in `[0,1]`;
- `--movement-key NAME=KEY` accepts `up`, `down`, `left`, and `right`;
- `--button-key NAME=KEY` accepts the configured action ontology;
- `--emergency-stop KEY` must be a supported normal key such as an alphanumeric key or function key.

Creation always writes `verified: false`. Measure the crop and UI regions from the user's own
training-mode emulator. Do not infer controls, timings, or mechanics from examples.

Validate schema only:

```powershell
python scripts/runtime.py calibrate-validate configs/local/local_training.yaml
```

After the user has manually checked every field and deliberately changed `verified` to `true`, require
the stronger validation:

```powershell
python scripts/runtime.py calibrate-validate configs/local/local_training.yaml --live-ready
```

Validation does not send input and does not mark a profile verified.

## 6. Benchmark native capture with input still disabled

This section is opt-in Work Order 002 activity and requires its explicit authorization. It never
authorizes input.

Open only the calibrated training-mode emulator, ensure window selection is unique, and run:

```powershell
python scripts/runtime.py capture-benchmark configs/local/local_training.yaml --frames 600
```

The JSON report includes elapsed time, FPS, p50/p95/p99 capture-to-consumer latency, duplicates,
dropped frames, and resident-memory change. A sample is never written unless explicitly requested:

```powershell
python scripts/runtime.py capture-benchmark configs/local/local_training.yaml `
  --frames 60 `
  --sample artifacts/capture_checks/explicit_sample.npy
```

Treat a saved sample as a private capture. Confirm it contains only the calibrated emulator region
and do not commit or share it.

## 7. Input activation boundary — not authorized

The Foundation exposes a programmatic input factory but no live gameplay command. Its default is
`DryRunInputBackend`; changing configuration alone cannot activate `SendInput`.

A future controlled live harness must pass an explicit `--live-input` value into the factory and must
already have:

1. a non-default profile that passes `--live-ready`;
2. exactly one selected emulator window;
3. positive focus verification before activation and before every batch;
4. fresh, non-frozen capture;
5. recognized character when a character-specific command is requested;
6. action-rate limits;
7. a successfully running emergency-stop listener;
8. a visible live-session indicator callback;
9. episode recording unless the user deliberately disables it for privacy.

Any rejection or exception releases held keys. Architecture V2 adds a preceding capability and
adapter path, but it does not weaken these checks. Do not add or invoke a live harness without a
separate authorized work order and a training/private-consent test plan.

## 8. Architecture V2 contract inspection

The V2 modules can be imported and tested without an emulator:

```powershell
python -m pytest tests/test_architecture_v2.py tests/test_episode_schema_v2.py -ra
```

These tests verify contract semantics, serialization, and safety routing only. They do not evaluate
screen perception or a gameplay policy. New recordings use manifest schema V2 and list unavailable
streams as `not_implemented`; do not change those statuses until a producer actually writes and
validates the stream.

The supported policy views are IR and SQ. IR is the intended primary path when opponent identity is
fresh and sufficiently confident; SQ is the fallback when it is not. The builder currently requires
an explicit view choice. Do not invent identity thresholds or claim automatic fallback before Work
Order 002 measures a passive identity estimator and records selection reasons.

## 9. Episode recovery

Normal, abort, injected-exception, and process-exit paths finalize the manifest. If a hard crash leaves
an open manifest, preserve the directory and run:

```powershell
python scripts/episode.py recover "<episode-directory>" --reason "<observed crash reason>"
python scripts/episode.py validate "<episode-directory>"
python scripts/episode.py inspect "<episode-directory>"
```

Recovery adds `incomplete_finalization`; it does not erase the failure or certify data quality.

## 10. Data locations

- local runtime profiles: `configs/local/`;
- raw recordings: `datasets/raw/`;
- processed data: `datasets/processed/`;
- experiment datasets: `datasets/training_sets/`;
- generated reports, explicit samples, and future checkpoints: `artifacts/`.

These contents are ignored by Git. Foundation episode storage uses a configured bounded `.npy` frame
fallback rather than claiming an encoded video backend.

## 11. Emergency recovery procedure

If any future live component becomes uncertain:

1. trigger emergency stop;
2. release every held key;
3. terminate the live runner;
4. preserve logs and the episode directory;
5. recover and validate the manifest without erasing quality flags;
6. record the failure in `docs/EXPERIMENT_LOG.md`;
7. reproduce with mocks or replay before another explicitly authorized live attempt.
