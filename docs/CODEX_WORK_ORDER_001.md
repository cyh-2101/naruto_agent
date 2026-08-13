# Codex Work Order 001 — Foundation Runtime and Recording Spine

## Objective

Implement the first durable capability slice inside the final architecture. The result must establish safe native-Windows runtime foundations and synchronized recording interfaces without beginning learned gameplay control.

This is not permission to collapse the repository into a toy MVP. Preserve all module boundaries and contracts described in `docs/ARCHITECTURE.md`.

## Required reading

Read before editing:

- `AGENTS.md`;
- `docs/PROJECT_BRIEF.md`;
- `docs/ARCHITECTURE.md`;
- `docs/ROADMAP.md`;
- `docs/DATA_SCHEMA.md`;
- `docs/SAFETY_AND_SCOPE.md`;
- current source and tests.

## Deliverables

### 1. Repository and environment diagnostics

Complete the system doctor so it reports, without crashing:

- operating system and Windows build where available;
- Python executable and version;
- CPU, RAM, GPU visibility, and optional CUDA/PyTorch information;
- installed capture and input backends;
- writable local config, dataset, and artifact directories;
- visible top-level windows that could be emulator candidates;
- whether the process is running natively on Windows or inside WSL;
- any incompatible or missing requirements with actionable messages.

The doctor must work in a reduced form on non-Windows systems for tests.

### 2. Window discovery contract and Windows implementation

Implement:

- a `WindowInfo` contract;
- a `WindowLocator` protocol;
- a mock locator;
- a native Windows locator using documented OS APIs or `pywin32`;
- filtering by title substring, process name, visibility, and minimum dimensions;
- deterministic selection rules and explicit ambiguity errors.

Do not hard-code one emulator brand.

### 3. Capture backend

Implement:

- a production capture backend suitable for native Windows, preferably DXCam/Desktop Duplication;
- explicit window/crop profile;
- monotonically timestamped `FramePacket` output;
- duplicate/frozen-frame detection;
- bounded queues and clean shutdown;
- sample-frame export only when explicitly requested;
- benchmark command reporting FPS, latency distribution, duplicates, memory growth, and dropped frames;
- mock capture for all automated tests.

Do not use repeated ADB PNG screenshots as the primary real-time backend.

### 4. Input backend and safety

Implement:

- native Windows normal-key input through a reliable OS input mechanism;
- dry-run backend;
- mock backend;
- key-down, key-up, timed press, and release-all;
- held-key tracking;
- focus check before every live action batch;
- action-rate limits;
- explicit `--live-input` opt-in;
- emergency-stop hotkey that immediately releases all held keys;
- process-exit and exception cleanup;
- no real input in unit tests.

The policy-facing interface must remain `ControlCommand` or a versioned successor. No direct key calls from policy code.

### 5. Local calibration profiles

Implement a CLI-first calibration workflow for:

- emulator window selection;
- capture crop;
- normalized UI regions;
- keyboard mapping;
- emergency-stop key;
- per-profile validation and versioning.

A minimal visual selector may be used, but avoid building a large GUI. Store real profiles under `configs/local/`, which is ignored by Git. Never overwrite example profiles.

### 6. Synchronized recorder spine

Implement a recorder capable of storing:

- encoded video or a bounded raw-frame fallback;
- frame index with timestamps;
- raw key events;
- derived control-state intervals;
- episode manifest;
- start, stop, abort, and crash-finalization paths;
- selected controlled character;
- configuration hashes and code commit when available;
- quality flags for dropped frames, timestamp gaps, and incomplete finalization.

Implement episode validation and inspection commands. Do not invent model or perception outputs yet.

### 7. Mock vertical loop

Provide a safe integration test or demo:

```text
mock capture -> placeholder observation -> dry-run policy output -> safety gate -> mock input -> recorder
```

It must run without Windows, a game, or an emulator and produce a valid temporary episode manifest.

### 8. Tests and documentation

Add tests for:

- configuration validation;
- timestamp monotonicity;
- ambiguous window selection;
- bounded capture queue;
- duplicate-frame detection;
- held-key cleanup;
- safety-gate rejection cases;
- emergency-stop state transition;
- episode finalization after an injected exception;
- no real-input path in the default test suite.

Run safe tests and static checks available in the environment.

Update:

- `README.md`;
- `docs/RUNBOOK.md`;
- `docs/PROJECT_STATUS.md`;
- `docs/DECISIONS.md` if a durable choice was made;
- `docs/EXPERIMENT_LOG.md` with commands and actual results.

## Out of scope for this work order

Do not implement:

- real game-state perception;
- hard-coded character mechanics;
- behavior cloning;
- PPO or other online RL;
- inverse dynamics;
- video scraping;
- world-model training;
- self-play;
- public/ranked automation;
- anti-cheat avoidance.

## Acceptance criteria

Work Order 001 is complete only if:

1. default commands are safe and dry-run;
2. automated tests do not send real input;
3. native-Windows components have graceful non-Windows behavior;
4. a mock end-to-end episode validates;
5. real input cannot activate without explicit opt-in and valid prerequisites;
6. every held key is released on normal exit, exception, focus loss, or emergency stop;
7. recorded timestamps are monotonic and quality-checked;
8. all three character configuration files still validate without fabricated mechanics;
9. documentation states exactly what was and was not tested;
10. Git contains no captures, datasets, credentials, or large generated artifacts.

## Final Codex report format

At completion, report:

1. files and components implemented;
2. tests and commands run;
3. results and any failures;
4. what was verified only with mocks;
5. what still requires the user’s native Windows emulator;
6. exact commands the user should run next;
7. risks or decisions needing attention;
8. the proposed scope of Work Order 002, without starting it.
