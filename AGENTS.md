# AGENTS.md

## Mission

Build a serious, screen-only, multi-character fighting-agent platform. The supported initial characters are `taka_sasuke`, `white_mask`, and `pain`. The system must learn shared combat knowledge while allowing character-specific perception templates, skills, timings, adapters, and policy heads.

## Authority order

When instructions conflict, follow this order:

1. Safety and scope rules in this file and `docs/SAFETY_AND_SCOPE.md`.
2. Architectural invariants in `docs/ARCHITECTURE.md`.
3. The active work order in `docs/`.
4. Roadmap and other documentation.
5. Existing implementation details.

Do not silently weaken higher-priority constraints.

## Hard scope restrictions

Allowed environments:

- training mode;
- game-provided AI practice;
- private matches with consenting friends.

Forbidden:

- ranked or public matchmaking;
- play against non-consenting people;
- reading or modifying game memory;
- code injection, DLL injection, hooks inside the game process, packet manipulation, or protocol reverse engineering;
- anti-cheat evasion or detection bypass;
- extracting information not visible to a normal player;
- automatic scraping or downloading of copyrighted videos;
- shipping credentials, account tokens, large datasets, game assets, videos, or model checkpoints into Git.

All live input code must default to dry-run. Real input requires an explicit command-line flag, valid calibration, window-focus verification, and an active emergency stop.

## Architectural invariants

1. Runtime, perception, state estimation, skills, policies, learning, data, and evaluation remain separable modules.
2. Model output never sends keys directly. It passes through an action scheduler and safety gate.
3. Every frame, input event, state estimate, policy decision, and outcome uses a monotonic timestamp.
4. Raw recordings are immutable. Derived data goes into versioned processed datasets.
5. Character mechanics are configuration-driven and marked unverified until calibrated.
6. Shared combat knowledge and character-specific knowledge are represented separately.
7. Temporal context is mandatory. Do not design a final policy around isolated frames.
8. Low-confidence or invalid state fails safe: neutral action, key release, and logging.
9. Tests never send real input unless a test is explicitly marked and manually enabled.
10. No feature is described as working until the relevant test or live verification is recorded.
11. Replacing a model must not require rewriting the runtime or data layer.
12. Development proceeds as capability slices inside the final architecture, not throwaway MVPs.

## Current development policy

The active task is `docs/CODEX_WORK_ORDER_001.md`. Do not start raw-pixel PPO, online reinforcement learning, self-play, a world model, or unlabeled-video pseudo-labeling during Work Order 001.

The first slice must create reliable contracts, configuration loading, safe runtime interfaces, diagnostics, recording schemas, and tests. It must leave extension points for the full architecture.

## Engineering standards

- Python 3.11 or 3.12 for the project environment.
- Type hints on public APIs.
- Prefer `dataclass`, `Protocol`, and Pydantic models where they make boundaries explicit.
- Use monotonic nanoseconds for runtime synchronization and UTC timestamps for human-readable metadata.
- Structured logging; no unexplained `print` calls in library code.
- Deterministic seeds where meaningful.
- Configuration validation at startup.
- Unit tests use mock backends and synthetic frames.
- Integration tests involving a real emulator must be opt-in.
- Keep dependencies narrow in Foundation.
- Avoid hard-coded window titles, coordinates, key maps, image dimensions, and character timings.
- Do not fabricate character mechanics. Unknown values remain `null`, disabled, or explicitly unverified.
- Do not overbuild a UI before the underlying contracts and runtime are stable.

## Required documentation discipline

After each meaningful implementation session, update:

- `docs/PROJECT_STATUS.md` — what actually works, what is blocked, and the next action;
- `docs/DECISIONS.md` — durable architectural decisions and rejected alternatives;
- `docs/EXPERIMENT_LOG.md` — commands, environment, results, failures, and artifacts;
- `README.md` or `docs/RUNBOOK.md` when commands change.

Never erase failures from the experiment log. Mark superseded decisions rather than silently deleting them.

## Definition of done for any task

A task is complete only when:

- implementation exists;
- safe automated tests pass;
- failure modes are handled;
- usage commands are documented;
- claims in `PROJECT_STATUS.md` match evidence;
- no real input is triggered by default;
- Git status contains no accidental datasets, captures, credentials, or generated binaries.
