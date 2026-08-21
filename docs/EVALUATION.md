# Evaluation Plan V2

## Evidence classes

Every result must state whether it is schema, unit/synthetic, mock integration, native passive,
offline model, bounded live-input, or human/product evidence. One class cannot be reported as
another.

## Runtime and safety

- monotonic frame and decision timestamps;
- capture freshness, duplicate/drop/freeze accounting;
- calibration and focus failures;
- held-key cleanup and emergency-stop behavior;
- action-rate, timeout, and stale-state rejection;
- proof that semantic actions traverse capabilities, adapter, scheduler, and SafetyGate.

Current evidence: safe unit/mock tests only. Native capture and input remain unverified.

## Estimate and temporal state

- false/zero versus unavailable discrimination;
- confidence calibration and threshold behavior;
- freshness/staleness and source/provenance completeness;
- temporal alignment and sequence continuity;
- passive accuracy for health, energy, position, phase, readiness, round state, and scene entities;
- explicit not-implemented, unknown, invalid, and stale rates.

No passive game accuracy has been measured yet.

## Observation views

- IR identity threshold behavior;
- SQ opponent-ID absence and configured self-ID presence;
- serialized key/value/provenance leakage audit;
- identical source state and dataset lineage across view comparisons;
- IR-to-SQ fallback correctness for unknown, stale, low-confidence, and conflicting identity.

Current evidence: synthetic contract and serialization tests only.

## Actions and capabilities

- all nine movement compositions;
- per-factor semantic-action accuracy when a future policy exists;
- capability-mask false accept/reject rates;
- temporary capability expiry;
- unsupported slot, deadline, and stale-capability rejection reasons;
- scheduler and safety decision agreement.

Current evidence: movement, rejection, and no-bypass unit tests; no character mechanic evidence.

## Data quality

- manifest/event schema validation and V1 readability;
- checksum and raw immutability;
- stream status correctness;
- episode-level splits and provenance;
- annotation review, class balance, missingness, and confidence distributions;
- no credentials, game assets, recordings, or checkpoints in Git.

## Future policy evaluation

Only after explicit authorization and dataset acceptance:

- held-out imitation metrics and temporal baselines;
- legality and calibration, not just action accuracy;
- familiar/unfamiliar opponent conditions for IR and SQ;
- identity-available, identity-missing, and identity-corrupted conditions;
- shared-backbone versus justified alternatives;
- competence, behavior profile fit, robustness, fairness, and safety as separate axes.

Win rate alone is insufficient. Shūkai or Kihan results are references, not baselines achieved here.

## Promotion gates

Contract implementation, technical validation, dataset acceptance, model promotion, live-input
authorization, and product acceptance are separate decisions. No automated test may self-approve the
next gate.
