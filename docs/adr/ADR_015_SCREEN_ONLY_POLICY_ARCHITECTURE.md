# ADR-015 — Screen-Only Policy Architecture V2

- Status: partially superseded by ADR-016 on 2026-08-22
- Date: 2026-08-21
- Scope: runtime/policy/data boundaries; no learning or live gameplay authorization

ADR-016 removes IQ and changes view routing to IR primary with SQ fallback. The IR/SQ/IQ text below
is retained as the historical decision record for this architecture checkpoint.

## Context

Work Order 001 established safe capture/input/recording interfaces around `ControlCommand`,
`ActionScheduler`, and `SafetyGate`. The earlier architecture described structured and visual paths,
a mandatory hierarchy, character skill packages, registries, and a world model, but it did not make
uncertainty, identity ablations, semantic action factors, or capability masks durable contracts.

The local Shūkai paper and project research note suggest useful high-level ideas: identity-conditioned
observation variants, Move/Skill/Direction heads, action masks, shared/generalized policies, and
separate behavior evaluation. The paper obtains its results from client-internal state and large PPO
and heterogeneous-league infrastructure, including information unavailable to a normal player. That
evidence cannot validate this project. The local Kihan code is a screen-perception prototype, but its
hard-coded single loop, direct PyAutoGUI control, single-frame observation, and reward behavior
conflict with project invariants.

## Decision

Adopt this final runtime boundary:

```text
capture -> perception adapters -> TemporalCombatState -> temporal/belief encoding
-> IR/SQ/IQ view -> shared temporal backbone -> character conditioning/adapter
-> factorized SemanticAction -> ActionCapabilities/mask -> character adapter
-> ActionScheduler -> SafetyGate -> input
```

The default policy view is SQ. IR and IQ are versioned ablation/evaluation views made from the same
state. `Estimate[T]` carries value/unavailability, confidence, timestamps, provenance, version, and
freshness. Scene entities are first-class screen-derived estimates.

The policy emits vertical, horizontal, skill, direction, hold, deadline, and cancel semantics. It
never sees keyboard bindings. `ControlCommand` remains a transitional downstream contract.

Use one shared temporal backbone with character conditioning and small character adapters/heads.
Do not build a full stack per character. `ActionCapabilities` handles calibrated, time-varying
legality and remains separate from runtime safety.

Strategic intent is optional auxiliary context, not a mandatory hierarchy. Dataset/policy/opponent
registries and `BehaviorProfile` are metadata contracts only. World models and league algorithms
remain experimental learning modules outside runtime.

## Consequences

- Perception must emit uncertainty rather than convenient defaults.
- Identity leakage becomes a schema/test concern, not only a model concern.
- Character mechanics can evolve without changing policy heads, but only after calibration.
- Replacing a model does not change capture, state, data, scheduler, or safety contracts.
- Episode schema must preserve raw evidence and version every optional derived stream.
- Legacy code remains operable during migration, but new policy work targets `SemanticAction`.

## Rejected alternatives

### Three independent character stacks

Rejected because shared combat knowledge, data lineage, evaluation, and runtime safety would drift.

### Mandatory strategic/tactical/execution controllers

Rejected as an architectural requirement. It adds latency and coordination assumptions before an
empirical need exists. Strategic intent remains optional.

### Policy emits ControlCommand or keys directly

Rejected because it entangles model output with character/emulator bindings and can bypass explicit
capability reasoning. Keys remain behind scheduler and SafetyGate.

### Use Shūkai client state or reproduce its PPO/HELT stack

Rejected because client-internal/hidden state violates screen-only scope, and no current work order
authorizes RL, self-play, leagues, or their compute/data assumptions.

### Move world model into core runtime

Rejected because it would make an experimental learner a safety-critical dependency and make model
replacement rewrite runtime/data layers.

### Port Kihan's monolithic PyAutoGUI loop

Rejected because it hard-codes capture, perception, policy, action, and input in one process and does
not preserve the project's dry-run and modularity invariants.

## Verification

The contract refactor is verified only by safe unit/mock tests covering estimate semantics,
freshness, IR/SQ/IQ identity boundaries, movement composition, capability rejection, enforced
scheduler/safety traversal, V2 episode serialization, V1 manifest readability, and the unchanged
Work Order 001 suite. It is not native perception, character, model, or gameplay evidence.
