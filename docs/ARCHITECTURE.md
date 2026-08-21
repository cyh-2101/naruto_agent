# Architecture V2 — Screen-Only Multi-Character Policy Platform

## Authority and evidence boundary

The runtime may use only pixels visible to a normal player and normal emulator input. It may not use
game memory, injected hooks, network traffic, hidden hitboxes, internal cooldowns, or other client
state. Every screen-derived value is an `Estimate[T]` with evidence and freshness; missing values
stay missing.

The V2 contracts are implemented and synthetic-tested. Perception adapters, learned models, native
capture performance, calibrated character mechanics, and real gameplay control are not thereby
implemented or verified.

## Approved runtime path

```text
Emulator
  -> Frame Capture
  -> Perception Adapters
  -> TemporalCombatState
  -> Belief / Temporal Encoder
  -> ObservationViewBuilder -> IR (primary) | SQ (fallback)
  -> Shared Temporal Backbone
  -> Character Conditioning / Adapter
  -> Factorized Semantic Action Heads
  -> SemanticAction
  -> ActionCapabilities + legality/action mask
  -> CharacterActionAdapter
  -> ActionScheduler
  -> SafetyGate
  -> InputBackend
```

No policy or model may call an input backend, key API, or emulator coordinate directly. The V2
`SemanticActionDispatcher` enforces the implemented tail of this path:

```text
SemanticAction -> ActionCapabilities -> CharacterActionAdapter
               -> ActionScheduler -> SafetyGate -> InputBackend
```

Capability rejection stops before adaptation. Safety rejection still applies after capability
acceptance. These are different decisions and both must be recorded when the recorder gains the V2
runtime streams.

## Side systems

The following systems observe or catalog runtime artifacts but do not bypass the runtime path:

- immutable raw episode recorder and versioned derived streams;
- dataset, policy, opponent, and evaluation registries;
- optional `BehaviorProfile` metadata for style and preference targets;
- calibration and character configuration packages;
- offline/manual evaluation and promotion evidence.

Learning jobs consume immutable datasets and emit candidates to registries. They do not become
runtime components merely by existing.

## Canonical state and uncertainty

`Estimate[T]` distinguishes a known false/zero from no value. It contains:

- `value`, or an explicit `unavailable_reason`;
- confidence;
- monotonic observation and validity timestamps;
- source, provenance, and optional source/model version;
- computed valid, unknown, invalid, stale, or not-implemented status.

`TemporalCombatState` is the only canonical policy-state source. It contains self and opponent
combatant estimates, relative geometry, round state, temporal/quality metadata, and tracked
`SceneEntity` estimates. Known action-phase names are supplied by `ActionPhase`, while the stored
phase is a string estimate so future calibrated phases do not require a core rewrite.

Low-confidence, stale, invalid, or unavailable state must yield a neutral decision or rejection.

## Observation views

`ObservationViewBuilder` derives both views from the same `TemporalCombatState`:

- IR (`identity_rich`): exposes self and opponent identity only when each identity estimate is fresh
  and above the configured confidence threshold;
- SQ (`self_qualified`): exposes the configured self identity and never opponent identity.

Hidden opponent-identity keys are absent from serialized SQ policy views; they are not serialized as
null. Provenance/source strings are retained in dataset records but omitted from policy projections
so identity cannot leak through an adapter name. Every view has a schema version and view version.

IR is the primary performance view because reliable legal information should not be discarded. SQ
is the runtime fallback when opponent identity is unknown, stale, or below threshold. In future
learning work, SQ also supports identity dropout so the shared backbone must understand visible
behavior instead of relying only on a character name. Both views share perception and policy
weights; they are not separate stacks.

The view resolver is future runtime work. The implemented builder currently constructs a requested
IR or SQ view and enforces its serialization boundary; it does not yet select views automatically.

## Implementation sequence and gates

1. **Current verified contracts:** preserve Work Order 001, `Estimate`, canonical state, explicit
   IR/SQ building, semantic actions, capabilities, scheduler/safety, and episode V2.
2. **Authorized passive Work Order 002:** validate capture/calibration, record user-operated data,
   measure identity/health/position estimates, populate state and both views, and evaluate missing,
   stale, low-confidence, and conflicting identity. No generated input or learning.
3. **View resolver after evidence:** select IR when the opponent identity estimate is usable;
   otherwise select SQ, and record the selected view plus reason. Thresholds come from measured
   calibration, not guesses.
4. **Separately authorized offline policy work:** train one shared temporal backbone primarily with
   IR while applying opponent-identity dropout to produce SQ robustness. Compare full, missing, and
   corrupted identity conditions. Candidate models remain unable to send input.
5. **Character integration:** add only evidence-backed capabilities and small adapters/heads for
   each character; keep semantic output and runtime/data contracts unchanged.
6. **Dry-run/shadow evaluation:** run policy decisions through capabilities, adapter, scheduler, and
   SafetyGate with input disabled; measure legality, latency, confidence, and fallback behavior.
7. **Future bounded input gate:** only a new explicit authorization may test real input in training
   mode after calibration, focus, emergency stop, recording, and failure recovery are verified.

Each step stops at its own Product Owner gate. Later steps are not authorized by this architecture.

## Policy structure

The intended policy structure is one shared temporal backbone, followed by character conditioning,
a small character adapter, and factorized heads. The factorized output is:

- vertical intent: neutral/up/down;
- horizontal intent: neutral/left/right;
- skill intent: none, normal attack, generic skill slots, substitution, summon, or scroll;
- optional skill direction;
- hold duration, deadline, cancel condition, and confidence.

Vertical and horizontal factors compose into the existing nine-way `MovementDirection` only after
the policy boundary. `LegacyControlAdapter` is a transitional semantic-to-`ControlCommand` bridge;
it maps generic slots but contains no keyboard bindings or character mechanics.

Strategic intent may be supplied as an auxiliary feature or head. It is not required to operate a
separate strategic, tactical, and execution controller.

## Character capabilities and adapters

Shared knowledge covers temporal interaction patterns, distance, pressure, defense, and resource
tradeoffs. Character-specific packages contain only configuration, perception templates, calibrated
capabilities, semantic-to-generic-control adaptation, timing evidence, and small learned adapters or
heads.

`ActionCapabilities` is time-bounded and versioned. It declares allowed factors and returns a mask
plus rejection reasons. It can represent a temporary mechanics-changing state by issuing a short
validity window and a different allowed set. It never infers or invents that state. The three current
character files remain unverified and therefore do not authorize character mechanics.

The platform must not create three independent perception-policy-runtime stacks.

## Data and registries

Episode manifest schema V2 reserves versioned streams for perception estimates, canonical state,
views, semantic actions, capabilities, masks/rejections, scheduler/safety decisions, and annotations.
Each stream states valid, absent, not implemented, unknown, invalid, or stale as applicable. Existing
V1 manifests remain readable.

`PolicyMetadata`, `OpponentMetadata`, and `DatasetMetadata` plus typed registries are catalog
contracts only. HELT, PFSP, league sampling, self-play, and policy promotion algorithms are not
implemented.

## Experimental modules outside runtime

World models, inverse dynamics, action-free video learning, online RL, self-play, and league training
are future research candidates. A world model, if ever authorized, must live under learning and emit
offline artifacts; it cannot become a prerequisite for capture, state construction, views, action
legality, scheduling, or safety.

The Shūkai paper motivates identity ablations, factorized actions, masks, and behavior evaluation.
Its hidden client state, hitbox information, PPO results, deployment claims, and distributed league
system are not transferable evidence for this screen-only project. Kihan is treated only as a
perception-prototype reference; its direct PyAutoGUI path, hard-coded monolith, single-frame policy,
and reward implementation are not adopted.

## Failure behavior

On stale capture, invalid calibration, uncertain required state, expired capabilities, unsupported
semantic action, lost focus, emergency stop, timeout, or excess action rate:

1. reject or choose neutral;
2. release held keys when an input backend is involved;
3. record the stage and reason when that V2 stream is implemented;
4. require fresh evidence before resuming.
