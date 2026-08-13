# Evaluation Plan

## Evaluation layers

### Runtime

- capture FPS and frame-time distribution;
- duplicate and dropped frames;
- capture-to-decision latency;
- decision-to-input latency;
- missed or stuck input rate;
- focus-loss and emergency-stop behavior;
- memory and CPU usage over long runs.

### Perception

- health estimation error;
- position error in normalized screen coordinates;
- active-character accuracy;
- round-phase accuracy;
- animation-state macro F1;
- calibration and expected calibration error for confidence;
- failure rate under visual effects and occlusion.

### Action execution

- requested versus executed action;
- timing error;
- successful action completion;
- interruption detection;
- blind continuation after miss;
- safe fallback frequency.

### Policy

- movement and button accuracy;
- macro F1;
- per-character confusion matrices;
- temporal consistency;
- closed-loop damage dealt and received;
- damage differential;
- successful hit confirmation;
- empty-skill frequency;
- substitution usage;
- inactivity;
- win/loss with the exact number of matches.

### Multi-character and lineup

- per-character performance;
- joint versus independent training;
- transfer to a held-out opponent condition;
- persistent lineup memory versus reset baseline;
- first-round observations changing later-round strategy.

### Human-like control

- measured reaction-delay distribution;
- execution error rate;
- aggression and retreat frequency;
- difficulty curve;
- consistency with configured style.

## Reproducibility record

Every report must state:

- code commit;
- dataset version;
- model version;
- emulator and capture profile;
- character configuration versions;
- random seed where applicable;
- number of episodes;
- opponent condition;
- whether evaluation was live, replayed, offline, or imagined.

## Promotion gate

A policy may be promoted to the default live candidate only if:

- no safety regression occurs;
- runtime and perception are within documented limits;
- it passes a fixed regression suite for all supported characters;
- evaluation includes enough episodes to state the sample size honestly;
- artifacts and metrics are saved in the policy registry.
