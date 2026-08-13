# Character System

## Design goal

The three initial characters share a common combat ontology but retain independent mechanics and execution knowledge. Adding a fourth character should require a new specification, calibration data, and optionally an adapter—not a copy of the repository.

## Shared knowledge

Examples:

- approach and retreat;
- vertical evasion;
- hit confirmation;
- knockdown and recovery;
- pressure and disengagement;
- opponent substitution inference;
- risk and distance reasoning;
- round and lineup context.

## Character-specific knowledge

Examples:

- visual identity and animation templates;
- skill variants and follow-ups;
- input timing ranges;
- cancel windows;
- preferred distance bands;
- legal action transitions;
- conditional combo graph;
- adapter or policy-head checkpoint;
- character-specific evaluation rules.

No exact mechanic is considered true until calibrated and recorded as verified.

## Character specification lifecycle

1. `declared` — identity exists, mechanics unknown;
2. `input_calibrated` — buttons and movement mappings verified;
3. `timing_calibrated` — action durations and recovery ranges measured;
4. `visual_calibrated` — templates and action phases labeled;
5. `script_verified` — scripted action and conditional sequence succeed;
6. `policy_ready` — learned policy passes closed-loop acceptance tests.

## Action ontology

Low-level movement:

- neutral;
- up, down, left, right;
- four diagonals.

Buttons:

- normal attack;
- skill 1;
- skill 2;
- ultimate;
- substitution;
- secret scroll;
- summon.

Macro actions are semantic requests such as:

- approach;
- retreat;
- side step;
- maintain distance;
- normal combo;
- use skill;
- continue on hit;
- abort on miss;
- substitution escape;
- pressure after hit;
- wait for recovery.

## Conditional combo graph

A sequence is a graph, not a blind list:

```text
skill_start
├── hit_confirmed ──► continuation choice
├── missed ─────────► disengage or defend
├── interrupted ────► recover
└── opponent_substituted ──► defensive response
```

Every node may specify:

- preconditions;
- action request;
- expected visual evidence;
- timeout;
- success edges;
- failure edges;
- safe fallback.

## Model routing

Recommended final organization:

```text
shared temporal visual encoder
+ shared structured-state encoder
+ shared belief and strategic policy
+ character embedding
+ character adapter
+ character skill executor
```

Required experimental baselines:

- three independent policies;
- shared trunk with separate heads;
- fully character-conditioned shared model.

The architecture should permit all three without changing the data pipeline.
