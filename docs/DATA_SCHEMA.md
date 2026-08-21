# Data Schema V2

## Principles

- Raw frames and user input records are immutable evidence.
- Derived artifacts live in versioned datasets; they never overwrite raw recordings.
- Runtime synchronization uses monotonic nanoseconds. Human metadata uses UTC.
- Every estimate distinguishes known false/zero from unavailable, invalid, stale, or unknown.
- Every model, policy, character config, calibration profile, view, and schema version is explicit
  when known; absent metadata remains null.
- V1 manifests stay readable. V2 does not reinterpret old data as newly available evidence.

## Episode layout

The Foundation recorder currently writes:

```text
episodes/<episode_id>/
  manifest.json
  frame_index.jsonl
  input_events.jsonl
  actions.jsonl
  frames/*.npy
```

The NumPy frames are a bounded fallback, not a production video claim. Checksums cover finalized
files. Existing recovery and validation behavior remains unchanged.

## Manifest schema V2

`EpisodeManifest` accepts schema 1 or 2. New recordings use schema 2 and include optional:

- model and policy versions;
- calibration profile and character-config versions;
- observation-view version;
- `EpisodeStreamDescriptor` entries.

Each stream descriptor has a role, its own schema version, a status, optional path, and reason. The
implemented recorder marks raw frames, frame index, input events, and legacy control intervals as
valid. It truthfully marks the reserved V2 runtime streams as not implemented:

- perception estimates;
- `TemporalCombatState`;
- observation views;
- semantic actions;
- action capabilities;
- action masks and rejection reasons;
- scheduler and SafetyGate decisions;
- annotations.

The status vocabulary is `absent`, `not_implemented`, `unknown`, `invalid`, `stale`, and `valid`.
`not_implemented` means the producer does not exist. `unknown` means the producer ran but could not
obtain the value. These must never be collapsed.

## Estimate record

An `EstimateRecord` contains:

```json
{
  "value": false,
  "confidence": 0.93,
  "observed_at_ns": 1000000000,
  "valid_until_ns": 1100000000,
  "source": "screen_adapter",
  "provenance": "calibration-profile-id",
  "source_version": "adapter-v1",
  "unavailable_reason": null,
  "status": "valid"
}
```

`false` and `0` are valid values. Missing values use null plus an unavailable reason. A value becomes
stale when evaluated after `valid_until_ns`; source records are not rewritten.

## Canonical state record

`TemporalCombatState.to_record()` serializes:

- schema/timestamp/sequence metadata;
- self and opponent identity, health, energy, position, velocity, action phase, substitution and
  named skill-readiness estimates;
- relative delta, distance, distance bucket, and screen-edge relation;
- round phase/timer/outcome;
- tracked scene entities with type, owner, position, velocity, and lifetime;
- frame freshness, duplicate/drop, and aggregate confidence quality metadata.

The contract can represent all fields as unavailable. It does not manufacture perception.

## Policy-view records

`ObservationViewRecord` stores view type, schema version, view version, timestamp, and policy payload.
IR and SQ are projections of the same state. Hidden opponent-identity keys must be absent in
serialized SQ payloads. Dataset evidence may retain provenance outside the policy payload. Future
records must also state why IR or SQ was selected, once automatic view resolution exists.

## Action and decision records

Typed V2 records exist for:

- factorized `SemanticActionRecord`;
- `ActionCapabilitiesRecord` with a time-bounded allowed set;
- `ActionMaskRecord` with per-factor booleans and reasons;
- `DispatchDecisionRecord` for scheduler or SafetyGate decisions.

The legacy `ControlStateInterval` remains for Work Order 001 compatibility. It is downstream of
semantic adaptation and must not become a policy output again.

`EpisodeRuntimeEvent` is a versioned envelope for future optional payload streams. A valid event
requires a payload; a not-implemented event requires a reason.

## Metadata registries

`DatasetMetadata`, `PolicyMetadata`, and `OpponentMetadata` record immutable identity/version,
provenance, supported characters, view type, training method, status, and related artifacts. The
in-memory typed registries reject duplicate keys. They do not implement training, league sampling,
promotion, or deployment.

## Dataset lifecycle

1. Record raw episode evidence.
2. Finalize and checksum it.
3. Validate timestamps, counts, schema, and checksums.
4. Create a versioned derived dataset with source episode IDs.
5. Split by episode/session/opponent conditions, never by adjacent frame.
6. Record annotation source and inter-rater or review evidence.
7. Register a candidate; require a separate Product Owner promotion decision.

Do not commit episodes, frames, videos, credentials, model checkpoints, or local calibration data.
