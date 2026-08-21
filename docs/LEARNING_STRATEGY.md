# Learning Strategy and Authorization Boundaries

## Current state

No learning algorithm was added or run in the Architecture V2 refactor. There is no trained policy,
behavior-cloning model, reinforcement-learning loop, self-play system, opponent sampler, or world
model in the approved runtime.

## Preconditions for any learning work

- an explicitly authorized work order;
- immutable, lawful, user-owned or consented data;
- accepted schema, timestamp, calibration, split, and label quality;
- a simple baseline and evaluation plan;
- candidate-only outputs with no live-input authority;
- reproducible metadata in dataset and policy registries.

## Recommended future sequence

1. Passive temporal representation and perception evaluation.
2. User-operated demonstration collection and dataset acceptance.
3. Offline behavior-cloning baselines with IR as the full-information view, SQ identity dropout, and
   reliable SQ fallback behavior.
4. Shared-backbone versus justified adapter/head baselines.
5. Only if separately authorized, offline improvement or action-free-video experiments.
6. Only after much later safety and Product Owner gates, bounded live-input research.

Do not begin with random raw-pixel PPO.

## Policy architecture for future candidates

All policy families must preserve the same boundary:

```text
versioned ObservationView -> shared temporal backbone -> character conditioning
-> factorized semantic heads -> SemanticAction
```

Strategic intent is optional auxiliary context or an auxiliary prediction head. It is not a required
three-controller hierarchy. Models never learn key bindings.

## Identity robustness plan

IR and SQ are controlled views from one state and one dataset lineage. IR is the primary candidate;
SQ is used for opponent-identity dropout during future training and for runtime fallback. Compare
them on held-out episodes, unfamiliar opponents, missing identity, and deliberately corrupted
identity. Audit SQ for identity leakage before attributing differences to conditioning.

## Registries are not leagues

The policy, opponent, and dataset registry contracts exist so future artifacts can be named,
versioned, and reproduced. They do not implement HELT, PFSP, policy pools, matchmaking, self-play, or
promotion. Those require distinct work orders and evidence.

## BehaviorProfile

Behavior profiles encode optional style targets such as aggression, caution, resource conservation,
and move preferences. Unknown values remain null. Verified profiles require an evidence reference.
Style alignment must be evaluated separately from competence, legality, and safety.

## World-model boundary

A world model is an optional future offline learning experiment. It must not be imported by capture,
state, view, action, scheduler, safety, or input modules. It must outperform simpler temporal
baselines before any promotion discussion. The current roadmap and Work Order 002 do not authorize
one.

## Research references

Shūkai supports investigating identity ablations, factorized actions, masks, heterogeneous metadata,
and behavior evaluation. Its client-internal state and PPO/HELT results are not project evidence.
Kihan can inform passive perception experiments, but its direct input, monolithic loop, single-frame
policy, and cumulative-reward behavior are rejected.
