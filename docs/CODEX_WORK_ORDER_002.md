# Codex Work Order 002 — Passive Observable Combat

## Status and authorization

Proposed only. Do not execute this work order without explicit Product Owner authorization.

This work order is passive: no generated gameplay input, learned control, or autonomous action is
permitted. The emulator, when used, is operated by the user in training mode or game-provided AI
practice while Naruto Agent input remains disabled.

## Objective

Validate native screen capture and local calibration, record a small user-operated demonstration,
and implement the first passive screen-derived estimates, `TemporalCombatState`, scene-entity schema,
and IR/SQ views with offline/manual evaluation and dataset validation.

The result must populate Architecture V2 contracts without weakening the Work Order 001 runtime,
recorder, or safety boundary.

## Required reading

- `AGENTS.md`;
- `docs/SAFETY_AND_SCOPE.md`;
- `docs/ARCHITECTURE.md`;
- `docs/DATA_SCHEMA.md`;
- `docs/CHARACTER_SYSTEM.md`;
- `docs/EVALUATION.md`;
- `docs/PROJECT_STATUS.md`;
- `docs/adr/ADR_015_SCREEN_ONLY_POLICY_ARCHITECTURE.md`;
- `docs/SHUKAI_KIHAN_ARCHITECTURE_IDEAS.md` as research context only.

## Deliverables

### 1. Native passive-capture evidence

- run diagnostics and enumerate the exact emulator/window selection;
- benchmark bounded native capture with input backend disabled;
- record resolution, frame rate, latency proxy, duplicates, drops, freezes, CPU/RAM, environment,
  and command output;
- export only an explicitly approved small sample, if needed, to an ignored local path;
- document failure as failure; do not substitute mock evidence.

### 2. Local calibration

- create or update an ignored local calibration profile without overwriting examples;
- validate window, crop, UI regions, dimensions, and config/profile versions;
- do not calibrate action timings or mechanics unless separately scoped and supported by evidence;
- keep input disabled throughout this work order.

### 3. User-operated demonstration recording

- record a short bounded episode while the user controls the game;
- use only training mode, game AI practice, or a consenting private match;
- preserve immutable raw frames/input events and synchronized monotonic timestamps;
- validate finalization, checksums, privacy, and Git ignore boundaries;
- do not fabricate missing input events or annotations.

### 4. Passive perception adapters

Implement only a narrow, explicitly labeled set that can be measured from the approved recording,
for example visible health, approximate position, round phase, or identity. Every adapter returns
`Estimate[T]` with confidence, observation/validity time, provenance, version, and unavailability
reason.

Do not claim or infer hidden cooldowns, hitboxes, internal action phases, or character mechanics.
Unsupported fields remain `not_implemented`; occluded or unreadable observations remain `unknown` or
`invalid` as appropriate.

### 5. TemporalCombatState and scene entities

- assemble one canonical state from passive estimates;
- preserve self/opponent, relative, round, sequence, freshness, and quality metadata;
- exercise `SceneEntity` records only if a visible entity is labeled and evaluated;
- otherwise keep the stream/schema present and values explicitly unavailable;
- add no fake projectile, summon, trap, or area-effect detector.

### 6. IR/SQ views

- build both views from the same canonical state;
- treat IR as primary when opponent identity is fresh and sufficiently confident;
- treat SQ as fallback when opponent identity is unknown, stale, low-confidence, or conflicting;
- enforce identity confidence/freshness in IR;
- verify SQ never serializes opponent ID;
- audit keys, values, provenance, adapter names, and nested payloads for identity leakage;
- version the view builder and stored view records.

Implement and test view-selection reasons only after passive identity estimates have measured
confidence/freshness behavior. Do not fabricate a resolver from synthetic identity quality.

### 7. Episode V2 integration

- populate only streams that are actually produced;
- record perception, state, view, calibration, character-config, and adapter/view versions;
- retain `not_implemented` for semantic actions, capabilities, masks, scheduler/safety decisions if
  they do not occur in this passive work order;
- keep V1 manifest validation and existing recovery behavior passing;
- write derived data to a versioned processed dataset, never over raw evidence.

### 8. Offline/manual evaluation

- define a small reviewed label set from the user's episode;
- report accuracy/error, missingness, invalid/stale rate, confidence calibration, and timestamp
  alignment for each implemented estimate;
- report view leakage audit results;
- report sample counts and uncertainty; do not generalize beyond the recording;
- register dataset metadata as candidate only. Do not promote it automatically.

### 9. Tests and documentation

Add safe tests for:

- native code paths through mocks and synthetic frames;
- estimate confidence, expiry, unknown/invalid/not-implemented distinctions;
- state sequence and scene-entity serialization;
- IR/SQ identity, fallback reasons, and nested serialization leakage;
- episode stream population and missing-stream truthfulness;
- raw immutability, timestamp ordering, V1 compatibility, and no-live-input behavior;
- failure paths for ambiguous window, stale frames, bad calibration, and corrupt datasets.

Run every safe existing test plus Ruff, compilation, and mypy when available. Native capture checks
are opt-in, bounded, and input-disabled.

## Explicitly out of scope

- generated or scripted gameplay input of any kind;
- live `SendInput`, even in training mode;
- character skill execution, combo calibration, or fabricated timings;
- behavior cloning, inverse dynamics, offline RL, PPO, online RL, self-play, HELT, PFSP, league
  sampling, or policy pools;
- world-model implementation or training;
- action-free video pseudo-labeling;
- automatic video scraping or dataset download;
- model/policy training, promotion, deployment, or gameplay-quality claims;
- ranked/public matchmaking or non-consenting opponents.

## Acceptance criteria

Work Order 002 can be technically complete only when:

1. native passive-capture evidence exists, or the work order is reported blocked without a mock
   substitution;
2. calibration and user recording are local, versioned, bounded, private, and validated;
3. implemented estimates have reviewed ground truth and measured errors;
4. unsupported fields remain explicitly unavailable;
5. one state produces leak-audited IR/SQ records, with measured evidence for any automatic fallback;
6. V2 episode streams, checksums, timestamps, and V1 compatibility pass;
7. every safe automated test passes and no test sends live input;
8. documentation claims match artifacts;
9. Git contains no recordings, frames, assets, credentials, calibrations, or checkpoints;
10. the Product Owner separately decides whether to accept the dataset and authorize any next stage.

Technical completion does not authorize behavior cloning or input.

## Final report format

Report exact environment, commands, artifacts and their ignored paths, sample counts, measured
results, failures, unimplemented fields, tests, Git status/commit, privacy review, and the next
Product Owner decision. Distinguish mock, native passive, offline/manual, and unverified evidence.
