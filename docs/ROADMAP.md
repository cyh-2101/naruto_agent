# Capability Roadmap

Every capability is a durable slice inside Architecture V2. Technical completion never grants live
input, dataset promotion, model promotion, or the next work order.

## Capability 0 — Foundation and V2 contracts

Status: implementation and safe synthetic verification complete.

- configuration, window discovery, mock/native capture boundaries, dry-run/native input factories;
- scheduler, SafetyGate, emergency-stop interfaces, calibration profiles;
- immutable bounded recorder, validation, recovery, and mock vertical loop;
- `Estimate[T]`, `TemporalCombatState`, `SceneEntity`, IR/SQ/IQ views;
- factorized `SemanticAction`, `ActionCapabilities`, semantic dispatcher;
- V2 episode stream contracts, metadata registries, and `BehaviorProfile`;
- V1 manifest readability and V2 schema tests.

This does not prove native capture, perception, mechanics, policy quality, or gameplay control.

## Capability 1 — Passive observable combat (proposed Work Order 002)

Requires explicit Product Owner authorization. No generated input.

- validate native capture in training mode while input remains disabled;
- create local calibration evidence;
- record user-operated demonstrations;
- implement passive perception adapters for a narrow labeled subset;
- populate `Estimate[T]`, `TemporalCombatState`, SceneEntity, and IR/SQ/IQ records;
- measure confidence/freshness, serialization leakage, timestamp alignment, and dataset validity;
- use offline/manual evaluation only.

Exit requires native evidence and truthful error accounting. It does not authorize imitation learning.

## Capability 2 — Calibrated character execution

Future authorization required.

- calibrate generic semantic slots and character-specific capabilities from user evidence;
- add adapter/mask tests for temporary mechanics-changing states;
- shadow or dry-run semantic scheduling first;
- separately approve any bounded training-mode input check.

No unverified timings or mechanics may be filled from memory or guesswork.

## Capability 3 — Offline demonstration learning

Future authorization required after Capability 1 dataset acceptance.

- behavior cloning baselines on immutable user demonstrations;
- shared temporal backbone with SQ default and IR/IQ ablations;
- factorized heads, legality metrics, calibration, held-out episodes, and cross-character tests;
- candidates remain unpromoted and cannot send live input.

## Capability 4 — Shared multi-character intelligence

- compare shared backbone plus small adapters against justified baselines;
- preserve dataset, runtime, and action contracts when changing models;
- evaluate familiar/unfamiliar opponent identity conditions without hidden state.

## Capability 5 — Offline research extensions

Optional, separately authorized experiments may include inverse dynamics, action-free video methods,
offline policy improvement, or a short-horizon world model. Each stays outside runtime, uses lawful
data, and must beat simpler baselines. A world model is never a required runtime dependency.

## Capability 6 — Opponent and policy registries

The metadata contracts already exist. Future work may add evaluation-backed candidate/promotion
workflows. HELT, PFSP, league sampling, and self-play are not implied by the registry contracts.

## Capability 7 — Lineup and human training-partner research

Only after prior safety, perception, action, and policy gates:

- round and active-character tracking;
- lineup-level resource reasoning;
- competence, behavior, fairness, robustness, and human feedback evaluation;
- bounded private/training use with explicit authorization.

No current artifact demonstrates this capability.
