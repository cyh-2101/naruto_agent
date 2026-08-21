# Project Status

## Current phase

Work Order 001 remains complete and mock-verified. Architecture V2 contracts are implemented and
synthetic-tested on branch `architecture/v2-screen-only-policy`. Work Order 002 exists only as a
passive proposal and has not started.

No learning, generated gameplay input, character-mechanic calibration, or real emulator interaction
occurred in the V2 refactor.

## Implemented

### Preserved Foundation

- validated configuration and declared/unverified packages for all three characters;
- window discovery, bounded capture interfaces, dry-run/mock/native input factory boundaries;
- `ActionScheduler`, `SafetyGate`, focus/rate/emergency-stop failure behavior;
- local ignored calibration profiles;
- bounded immutable raw-frame episode recorder, checksums, validation, recovery, and mock loop.

### Architecture V2 contracts

- `Estimate[T]` with confidence, observation/validity timestamps, source, provenance, version,
  unavailable reason, and computed freshness/status;
- `TemporalCombatState`, self/opponent combatants, relative/round/quality metadata, and
  `SceneEntity` contracts;
- one `ObservationViewBuilder` for versioned IR/SQ/IQ policy payloads;
- factorized `SemanticAction`, nine-way movement composition, deadline/cancel fields;
- time-bounded `ActionCapabilities`, factor masks, and rejection reasons;
- transitional `LegacyControlAdapter` and enforced V2 semantic dispatch through scheduler/safety;
- shared temporal backbone, character conditioning, factorized-head, temporal-policy, and adapter
  Protocol boundaries;
- optional `BehaviorProfile`;
- typed policy/opponent/dataset metadata and duplicate-rejecting registries;
- episode manifest schema V2, optional stream descriptors/statuses, typed observation/action/
  capability/mask/dispatch records, and V1 manifest readability;
- Architecture V2 ADR and passive-only proposed Work Order 002.

## Verified on 2026-08-21

- Python 3.12.13 virtual environment;
- final pre-commit safe suite: `64 passed in 0.73s`;
- all original 40 Work Order 001 tests remain in the passing suite;
- Ruff: `All checks passed!` before documentation-only edits;
- bytecode compilation of `src` and `tests` succeeded;
- tests cover known false/zero versus unavailable, confidence/freshness/staleness, IR/SQ/IQ identity
  serialization, low-confidence identity omission, all movement compositions, optional strategic
  intent, capability rejection/expiry, scheduler/SafetyGate no-bypass, scene-entity and V2 episode
  round trips, V1 readability, and no live input;
- mock recorder now emits manifest schema V2 and explicitly marks unimplemented V2 streams instead
  of fabricating their payloads;
- the original user-provided Shūkai/Kihan research note and local 21-page Shūkai paper were read as
  references; only architecture ideas compatible with screen-only scope were adopted.
- native doctor completed without capture or input: no visible emulator candidates; DXCam,
  pywin32, pynput, OpenCV, and PyTorch were missing; local paths were writable;
- the eight-frame mock demo finalized with zero input events, eight neutral control intervals, the
  expected raw-frame fallback flag, and no validation errors.

## Verification limitations and recorded failures

- the first test attempt failed during collection because the existing virtual environment lacked
  the editable project and Pydantic; this was an environment failure, not a test result;
- two `pip install -e ".[dev]"` attempts stalled while downloading the 11.2 MB mypy wheel; the
  stalled process was terminated, core dependencies were restored with `pip install -e .`, and
  mypy remains unavailable;
- the bundled PDF-to-image wrapper referenced a missing Poppler path, so selected-page visual
  rendering failed; the PDF text layer was read and the relevant pages were located;
- no native emulator window, DXCam capture, crop, latency, physical emergency stop, or `SendInput`
  path was exercised;
- no local real calibration, user demonstration, passive game perception, or reviewed label set
  exists;
- all character mechanics, variants, timings, capabilities, and behavior profiles remain
  unverified;
- there is no shared learned backbone implementation, trained model, policy quality evidence,
  behavior cloning, RL, self-play, HELT/PFSP, world model, or policy promotion/deployment.

## Compatibility and deprecation

`PerceptionState`, `BeliefState`, `PolicyOutput`, `MacroActionRequest`, `ControlCommand`, and the
Foundation mock demo remain operational. They are compatibility contracts, not the target for new
policy work. New policy code must target `ObservationView -> SemanticAction`. `ControlCommand`
remains downstream of a character adapter until a later migration removes the legacy bridge.

## Immediate next decision

The Product Owner may review and authorize `docs/CODEX_WORK_ORDER_002.md`. If authorized, the next
work is native passive capture/calibration, a bounded user-operated demonstration, narrow measured
perception, state/view recording, and offline/manual dataset evaluation. Input must remain disabled.

Do not proceed to character execution or learning from this architecture checkpoint.
