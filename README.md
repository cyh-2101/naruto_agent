# Naruto Agent Lab

Naruto Agent Lab is a screen-only, multi-character fighting-agent research platform for
`taka_sasuke`, `white_mask`, and `pain`. It preserves one shared temporal combat architecture while
allowing character-specific perception templates, calibrated capabilities, timings, adapters, and
small policy heads.

The repository currently contains a mock-verified Foundation runtime/recording spine and
synthetic-tested Architecture V2 contracts. It does **not** contain game perception, a trained
policy, verified character mechanics, autonomous gameplay, reinforcement learning, self-play, or a
runtime world model.

## Safety boundary

Use is limited to training mode, game-provided AI practice, and private matches with consenting
friends. Ranked/public automation, non-consenting opponents, game memory, injection, hooks, packets,
hidden-state extraction, anti-cheat bypass, and automatic copyrighted-video scraping are forbidden.

Input is dry-run by default. Real input requires separate explicit authorization, valid calibration,
unique focused-window verification, fresh capture, an active emergency stop, and a visible live
indicator. No current work order authorizes generated gameplay input.

## Architecture V2

```text
Frame Capture -> Perception Adapters -> TemporalCombatState
-> ObservationViewBuilder (IR primary | SQ fallback)
-> Shared Temporal Backbone -> Character Conditioning / Adapter
-> Factorized SemanticAction -> ActionCapabilities / mask
-> CharacterActionAdapter -> ActionScheduler -> SafetyGate -> InputBackend
```

`Estimate[T]` makes confidence, freshness, provenance, and unavailable values explicit. Policies
never see key bindings. IR uses both identities only when opponent identity is fresh and sufficiently
confident. SQ keeps configured self identity but hides opponent identity, providing a safe fallback
and a future identity-dropout training view.

Recorders and dataset/policy/opponent/evaluation registries are side systems. Learning jobs and world
models, if ever authorized, remain outside runtime and cannot bypass scheduler or safety.

## Implemented components

- validated base/emulator/character configuration;
- Win32 window discovery contracts and bounded DXCam interface;
- dry-run, mock, and explicit-opt-in Win32 input backends;
- scheduler, SafetyGate, emergency-stop/focus/rate failure behavior;
- local ignored calibration profiles;
- immutable bounded episode recorder, checksums, validation, recovery, and mock demo;
- `Estimate`, `TemporalCombatState`, `SceneEntity`, and IR/SQ views;
- factorized `SemanticAction`, capabilities/mask decisions, and semantic dispatcher;
- typed metadata registries, optional `BehaviorProfile`, and episode schema V2;
- V1 manifest compatibility and 64 safe automated tests.

These are contracts and mock/synthetic evidence, not native emulator or policy-performance evidence.

## Quick start

Use Python 3.11 or 3.12 on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/doctor.py --project-root .
python -m pytest -ra
python -m ruff check .
python -m mypy src/naruto_agent
python -m compileall -q src tests scripts
python scripts/runtime.py mock-demo --frames 8
```

The safe suite uses mocks, synthetic frames, and temporary directories. If mypy is not installed,
report that limitation; do not represent Ruff or compilation as a substitute.

Native packages are separate:

```powershell
python -m pip install -e ".[dev,windows]"
```

Installing them does not authorize capture or input. See [the runbook](docs/RUNBOOK.md),
[current status](docs/PROJECT_STATUS.md), and [Architecture V2](docs/ARCHITECTURE.md).

## Next work order

[Work Order 002](docs/CODEX_WORK_ORDER_002.md) is proposed but not started. It is passive-only:
native capture validation, local calibration, a user-operated demonstration, narrow measured
perception, state/view recording, offline/manual evaluation, and dataset validation. It excludes all
generated input and learning.

项目负责人可在每个 Stage 或架构检查点后把 [learners.md](learners.md) 发给 ChatGPT，让它只按已验证能力教学。
