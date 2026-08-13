# Project Status

## Current phase

Work Order 001 Foundation implementation is complete and mock-verified. Native emulator capture and
live-input validation remain blocked on a visible training-mode emulator, a real local calibration,
and optional Windows packages. No learned gameplay work has started.

## Implemented

- strict cross-layer contracts with positive monotonic timestamps;
- validated base, emulator, and all three character configurations;
- deterministic window discovery contracts, mock locator, and native Win32 locator;
- title substring, exact process name, visibility, and minimum-size filtering with explicit
  not-found and ambiguity errors;
- high-resolution monotonic runtime clock based on `QueryPerformanceCounter`;
- mock capture and bounded native DXCam capture with duplicate/frozen detection, oldest-frame drop
  policy, shutdown, explicit `.npy` sample export, and benchmark metrics;
- dry-run and mock input plus an explicit-opt-in Win32 `SendInput` backend;
- held-key tracking, timed press, release-all, focus checks, action-rate limiting, process/exception
  cleanup, emergency-stop latching/listening, and visible-session callback requirement;
- dry-run-by-default input factory, action scheduler, and expanded fail-safe reasons;
- CLI-first local profile creation/validation with versioning, normalized regions, crop and key
  fields, ignored storage, and no example overwrite;
- bounded immutable raw-frame recording fallback, frame/input/control JSONL, atomic manifests,
  configuration hashes, optional Git commit, checksums, quality flags, normal/abort/exception/process
  finalization, recovery, validation, and inspection;
- explicit placeholder observation and neutral zero-confidence policy output for the mock vertical
  loop only;
- native/reduced doctor reporting OS/build, runtime, CPU, RAM, GPU, optional PyTorch/CUDA, available
  backends, writable directories, window candidates, and actionable missing requirements.

## Verified on 2026-08-13

- Python 3.12.13 on native Windows 11 build 26200;
- final rerun: `40 passed in 0.99s` for the full default safe test suite;
- Ruff completed with `All checks passed!`;
- bytecode compilation of `src`, `tests`, and `scripts` completed successfully;
- all three character YAML files validate as `declared`, `verified: false`, with every skill
  unverified;
- reduced non-Windows doctor behavior is covered by an automated test;
- native doctor completed without crashing and reported 32 logical CPU cores, 15.22 GiB RAM,
  `QueryPerformanceCounter` at 100 ns reported resolution, writable local/config/data/artifact paths,
  and an NVIDIA GPU visible to `nvidia-smi`;
- mock eight-frame vertical episode finalized and validated with eight neutral control intervals,
  zero input events, no validation errors, and only the expected `raw_frame_fallback` quality flag;
- mock benchmark plumbing reported 100 frames, 9 intentional duplicates, 0 drops, latency percentiles,
  memory delta, and elapsed time. Its synthetic FPS is not a production performance claim.

## Not verified or not implemented

- no visible emulator candidate was present during the native doctor run;
- DXCam, pywin32, pynput, OpenCV, and PyTorch were not installed in the verification environment;
- real DXCam capture, queue behavior under a native producer, FPS/latency/memory stability, crop
  correctness, and sample export were not tested against an emulator;
- `SendInput`, focus-loss cleanup on an actual window, and the physical emergency-stop hotkey were
  not invoked;
- no real local calibration exists and no example profile was modified;
- mypy was not run because its wheel download repeatedly timed out; tests, Ruff, and Python
  compilation passed, but they do not replace strict type checking;
- this directory was not recognized as a Git worktree, so commit capture and a Git-status audit were
  unavailable. A filesystem audit found no repository captures, credentials, datasets, videos, or
  model checkpoints outside ignored local/runtime directories;
- encoded video is not implemented; Foundation uses the accepted bounded raw-frame fallback;
- real perception, character mechanics/timings, scripted game skills, learned policies, imitation
  learning, reinforcement learning, action-free video learning, world models, self-play, and lineup
  execution remain out of scope and absent.

## Immediate next action

Create or restore a Git repository, install the Windows extra in Python 3.11/3.12, open only a
training-mode emulator, rerun the doctor, create an **unverified** local profile, and run the capture
benchmark with live input still disabled. Do not test real keys until the profile, unique window
selection, focus check, emergency stop, recording, and visible-session behavior are manually
verified and explicitly authorized.
