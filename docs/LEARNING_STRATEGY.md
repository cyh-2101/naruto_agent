# Learning Strategy

## Guiding rule

Do not rely on one learning method. Each data source solves a different problem.

## Stage A — Temporal visual representation

Use frame sequences from user-supplied gameplay to learn motion- and action-sensitive features. Candidate objectives may include temporal contrast, masked-frame modeling, future-feature prediction, and action-phase classification.

Output: a versioned visual encoder that can be evaluated separately.

## Stage B — Behavior cloning

Train on synchronized human demonstrations.

Inputs:

- recent frames or visual embeddings;
- structured perception state;
- previous action;
- character ID and optional adapter.

Outputs:

- movement;
- button or macro action;
- optional duration and confidence.

Requirements:

- temporal context;
- episode-level splits;
- class imbalance handling;
- per-character and joint metrics;
- closed-loop evaluation, not only offline accuracy.

## Stage C — Inverse dynamics and action-free video

Train an inverse dynamics model on labeled transitions:

```text
(previous visual context, next visual context, character context) -> action distribution
```

Apply it only to user-supplied action-free videos. Retain soft distributions and confidence. Filter or down-weight uncertain pseudo-labels.

A second experimental route may learn latent actions first and map them to real actions using the labeled subset.

## Stage D — State-only value learning

Even when exact actions cannot be inferred, trajectories can teach which states tend to lead toward advantage or danger. Learn state or belief value with explicit uncertainty and avoid treating edited highlight clips as unbiased trajectories.

## Stage E — Offline policy improvement

Build an immutable replay dataset from:

- human demonstrations;
- scripted baseline runs;
- learned-policy runs;
- consenting private matches;
- confidence-filtered pseudo-labeled video.

Compare conservative offline methods against behavior cloning. All transitions retain provenance.

## Stage F — Limited online refinement

The emulator is slow and cannot be treated as a high-throughput simulator. Closed-loop interaction should primarily correct:

- compounding imitation errors;
- missed attacks and interruptions;
- unseen opponent behavior;
- real input latency;
- perception errors.

Begin from a competent imitation policy and macro actions. Do not begin from random raw-pixel PPO.

## Stage G — World model

Learn short-horizon state and outcome prediction. Validate error versus horizon before using imagined rollouts. Never present model-generated experience as real experience.

## Stage H — Continual and multi-character learning

Use replay and regression evaluation to avoid losing earlier character skills. Track positive and negative transfer. Character adapters may be frozen, fine-tuned, or expanded based on evidence rather than assumption.

## Mandatory baselines

- scripted controller;
- behavior cloning per character;
- behavior cloning jointly;
- shared encoder with separate heads;
- joint character-conditioned policy;
- demonstration-only versus demonstration-plus-video;
- no-belief versus belief-state policy;
- flat versus hierarchical control.

## Evaluation caution

Offline action accuracy does not prove gameplay competence. Every model report must distinguish:

- offline held-out metrics;
- scripted-scenario closed-loop metrics;
- full-match metrics;
- number and type of evaluation episodes;
- real versus simulated or imagined outcomes.
