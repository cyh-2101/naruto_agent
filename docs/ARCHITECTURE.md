# Architecture

## System overview

```text
Windows emulator
    │ frames                                  ▲ safe key commands
    ▼                                         │
Runtime I/O ──► Perception ──► Belief & Memory ──► Hierarchical Decision
    │                 │                │                   │
    │                 │                │                   ▼
    │                 │                └────► Opponent Model / Lineup Memory
    │                 │                                    │
    │                 └──────────────► Character Context    ▼
    │                                                 Skill System
    │                                                      │
    └────────► Recorder ◄──────── all typed events ◄──── Scheduler & Safety
                    │
                    ▼
              Versioned Data Lake
                    │
       ┌────────────┴──────────────────────────────┐
       ▼                                           ▼
Representation / Imitation / Offline Learning   Evaluation / Policy Registry
       │                                           │
       └────────────► optional World Model ◄────────┘
```

## Layer 1: Runtime I/O

Responsibilities:

- emulator-window discovery and tracking;
- low-latency frame capture;
- monotonic timestamps;
- input abstraction and key release;
- focus and frozen-frame checks;
- action scheduling;
- emergency stop;
- synchronized episode recording;
- replay using recorded events.

Interfaces:

- `CaptureBackend`;
- `InputBackend`;
- `WindowLocator`;
- `ActionScheduler`;
- `SafetyGate`;
- `EpisodeRecorder`.

No model may call the input backend directly.

## Layer 2: Perception

Perception uses two complementary paths.

### Structured path

Estimates interpretable variables such as:

- self and opponent position;
- relative displacement and distance;
- health;
- visible readiness indicators;
- attack, movement, hit, knockdown, recovery, and round phase;
- current controlled character;
- confidence for every estimate.

Simple calibrated computer vision is preferred where it is more reliable than a neural model.

### Latent visual path

A temporal encoder maps a recent frame sequence to a learned embedding:

```text
z_t = VisualEncoder(frames[t-k:t])
```

This preserves information that is difficult to hand-label, including animation phase, effect motion, and subtle pre-action cues.

The policy observation is hybrid:

```text
observation_t = structured_state + visual_latent + previous_action + character_context
```

## Layer 3: Belief state and opponent model

The game is partially observable. The system maintains a temporal belief rather than trusting one frame.

Examples of latent beliefs:

- probability that opponent substitution is available;
- probability that opponent skills are available;
- current combo phase;
- opponent aggression and preferred approach patterns;
- risk estimate;
- uncertainty and stale-observation indicators.

Initial implementation may use rules plus a GRU. The interface must allow replacement by a temporal transformer or state-space model.

## Layer 4: Hierarchical decision system

Three timescales are separated.

### Strategic policy

Runs approximately 1–3 decisions per second and selects intents such as:

- pressure;
- bait skill;
- bait substitution;
- defend;
- retreat;
- wait for cooldown;
- punish;
- escape;
- finish combo;
- save resources.

### Tactical policy

Runs approximately 5–10 decisions per second and selects macro actions, target distance, approach direction, skill choice, continuation, or substitution.

### Execution policy and scheduler

Runs at the control rate and converts a macro action into legal, timed movement and button events. It monitors hit confirmation, animation phase, interruption, timeout, and focus.

## Layer 5: Character skill system

General combat knowledge is shared. Character-specific knowledge lives in a `CharacterSpec` package:

```text
CharacterSpec
├── identity and aliases
├── visual templates
├── enabled low-level actions
├── skill definitions
├── timing ranges
├── animation phases
├── legal transitions
├── conditional combo graph
├── preferred distance model
├── character adapter reference
└── evaluation rules
```

Character data must not be scattered through Python conditionals.

## Layer 6: Lineup manager

The lineup manager persists context across character changes:

- active character and round index;
- previous round outcomes;
- opponent style estimates;
- observed substitution habits;
- repeated opening actions;
- risk and resource strategy for the next character.

This layer distinguishes a true three-character system from three unrelated policies.

## Layer 7: Learning system

The learning pipeline is staged but shares one data contract:

1. video representation pretraining;
2. behavior cloning from synchronized demonstrations;
3. inverse dynamics from labeled transitions;
4. pseudo-action or latent-action learning from action-free videos;
5. value learning from state-only trajectories;
6. offline RL from accumulated transitions;
7. limited closed-loop refinement;
8. continual learning with regression evaluation.

No single algorithm is assumed to remain permanent.

## Layer 8: World model

A short-horizon model estimates:

```text
p(next_state, outcome | belief_state, macro_action)
```

Uses:

- representation learning;
- hit and outcome prediction;
- short imagined rollouts;
- tactical evaluation;
- data-efficiency experiments.

It is not treated as a perfect replacement for the real game because hidden state cannot be fully reconstructed from pixels.

## Layer 9: Policy registry, opponent pool, and evaluation

Every policy has:

- immutable version ID;
- training dataset version;
- code commit;
- configuration hash;
- metrics;
- supported characters;
- inference requirements.

The opponent pool may contain scripted opponents, fixed game AI conditions, historical policies, recorded behavior models, and consenting humans. A component is not called self-play unless both sides are actually controlled.

## Cross-cutting contracts

The minimum stable contracts are:

- `FramePacket`;
- `InputEvent`;
- `PerceptionState`;
- `BeliefState`;
- `StrategicDecision`;
- `MacroActionRequest`;
- `ControlCommand`;
- `PolicyOutput`;
- `EpisodeManifest`;
- `EpisodeTransition`.

Model and backend replacements must preserve or version these contracts.

## Failure behavior

Any of the following blocks live actions and releases held keys:

- missing focus;
- invalid calibration;
- stale or frozen capture;
- unrecognized active character when character-specific action is required;
- policy timeout;
- emergency stop;
- explicit dry-run;
- safety-gate failure.

Low perception confidence produces neutral behavior or a separately calibrated safe fallback, never an aggressive guess.
