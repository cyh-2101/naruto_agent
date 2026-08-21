# Character System V2

## Design rule

The platform has one shared temporal combat architecture, not three complete character stacks.
Character-specific knowledge is configuration-driven and remains unverified until calibrated from
the user's own lawful training-mode evidence.

## Shared knowledge

- temporal motion and interaction representation;
- relative geometry, distance, pressure, defense, and resource tradeoffs;
- the IR/SQ/IQ observation schemas;
- factorized vertical, horizontal, skill, and direction heads;
- scheduler, SafetyGate, episode schema, registries, and evaluation contracts.

## Character-specific knowledge

- visible identity and animation templates;
- local calibration references;
- semantic-slot capabilities and temporary capability changes;
- generic semantic-to-control adaptation;
- verified timing, cancel, and readiness evidence;
- a small conditioning adapter or policy head;
- optional verified behavior profile.

None of these authorizes keyboard bindings inside a policy.

## Current characters

`taka_sasuke`, `white_mask`, and `pain` have declared schema-valid YAML packages. Their skill timing,
variants, readiness cues, preferred distances, macros, combo graphs, and evaluation rules remain
unverified or empty. The V2 refactor did not fill them.

## Semantic action ontology

Policies emit `SemanticAction`:

- vertical: neutral/up/down;
- horizontal: neutral/left/right;
- skill: none, normal attack, generic skill slots, ultimate, substitution, scroll, summon, or
  extensible subskill slots;
- optional direction 1–8;
- hold duration, deadline, cancel condition, confidence.

`LegacyControlAdapter` maps only currently generic slots to `ControlCommand`. It contains no key map
and raises on unmapped subskills. Character adapters may add calibrated interpretations later, but
they must not guess mechanics.

## ActionCapabilities

Capabilities answer “is this semantic factor available now?” They are distinct from SafetyGate,
which answers “may any input be sent safely now?”

A capability snapshot declares time-bounded allowed vertical/horizontal/skill/direction sets, a
version/source, and rejection reasons. Temporary mechanics-changing states can be expressed by a new
short-lived snapshot after a screen-derived state estimate supports it. Without evidence, the
unverified default permits only neutral factors.

## Identity conditioning

- IR may condition on fresh, confident self and opponent identities.
- SQ, the default, conditions on configured self identity and hides opponent identity.
- IQ hides both identities.

All use the same `TemporalCombatState` and shared backbone. A model replacement must not require a
new recorder or runtime.

## Lifecycle

1. declared — schema valid, mechanics not trusted;
2. observed — user evidence exists but is not yet accepted;
3. calibrated — bounded fields have evidence and tests;
4. candidate — adapter/policy artifact exists offline;
5. validated — offline/manual acceptance evidence exists;
6. promoted — separate Product Owner authorization.

No current character is calibrated, validated, or promoted.
