# Capability Roadmap

This roadmap builds the final system in durable capability slices. Each slice must preserve the architecture and produce reusable data, tests, and interfaces.

## Capability 0 — Foundation and observability

Deliver:

- typed core contracts;
- configuration loading and validation;
- native Windows environment doctor;
- window discovery abstraction;
- capture and input interfaces with mock backends;
- dry-run-first safety gate and emergency stop;
- synchronized recording schemas;
- structured logging;
- unit tests and an experiment log.

Exit evidence:

- safe tests pass;
- mock capture-to-policy-to-scheduler loop runs;
- no automated test sends real input;
- invalid state fails safe;
- configuration for all three characters validates while remaining uncalibrated.

## Capability 1 — Calibrated runtime and observable combat

Deliver:

- interactive window, crop, UI-region, and control calibration;
- real low-latency capture benchmark;
- explicit real-input opt-in;
- episode recorder and replay viewer;
- first structured state estimates: health, round phase, active character, approximate positions;
- debug overlay and confidence reporting.

Exit evidence:

- capture reaches a documented stable rate on the user’s emulator;
- action latency and missed-input rate are measured;
- recorded frames and key events are time aligned;
- replay reproduces event timing in dry-run;
- perception metrics are measured on a labeled sample.

## Capability 2 — Character skill execution

Deliver:

- calibrated skill definitions for all three characters;
- action ontology and macro-action interface;
- conditional combo graphs;
- execution monitor with hit/miss/interruption paths;
- scripted baseline using shared combat states and character specs.

Exit evidence:

- each character completes all calibrated actions and at least one conditional sequence;
- no blind fixed combo continues after a detected miss or interruption;
- character switching routes to the correct configuration;
- every live run is recorded and reviewable.

## Capability 3 — Human demonstration learning

Deliver:

- synchronized demonstration collection workflow;
- quality checks and episode-level train/validation split;
- temporal behavior-cloning baseline;
- per-character and joint-training experiments;
- closed-loop policy runner with confidence fallback.

Exit evidence:

- policy outperforms random and scripted baselines on defined metrics;
- closed-loop failures are categorized;
- offline metrics and live performance are reported separately;
- model version and dataset version are traceable.

## Capability 4 — Shared multi-character intelligence

Deliver:

- shared temporal visual encoder;
- shared combat-state encoder;
- character embedding or adapter routing;
- shared strategic policy and character-specific tactical/execution outputs;
- transfer and ablation experiments.

Exit evidence:

- compare joint model, shared-trunk/separate-head model, and three independent policies;
- quantify positive or negative transfer;
- adding a character does not require duplicating the runtime or data pipeline.

## Capability 5 — Learning from action-free video

Deliver:

- legal user-supplied video ingestion;
- temporal representation pretraining;
- inverse dynamics trained on labeled demonstrations;
- confidence-filtered pseudo-actions or latent-action discovery;
- state-only value learning;
- controlled comparison against demonstration-only training.

Exit evidence:

- report whether video pretraining reduces labeled demonstrations or closed-loop matches;
- report pseudo-label confidence and failure modes;
- preserve a negative result if no benefit is observed.

## Capability 6 — Offline improvement and world model

Deliver:

- versioned replay dataset containing human, scripted, and learned-policy transitions;
- offline policy improvement baseline;
- short-horizon dynamics and outcome model;
- imagined-rollout experiments restricted to validated horizons.

Exit evidence:

- model calibration and prediction error are reported by horizon;
- imagined data is never mixed with real data without provenance;
- online evaluation verifies whether offline/world-model gains transfer.

## Capability 7 — Opponent adaptation and policy pool

Deliver:

- opponent feature and style model;
- historical policy registry;
- opponent sampling and targeted weakness evaluation;
- regression suite preventing catastrophic loss of earlier skills.

Exit evidence:

- performance is measured across multiple opponent conditions;
- adaptation is compared with a no-memory baseline;
- policy-pool claims correspond to saved, reproducible versions.

## Capability 8 — Lineup-level intelligence

Deliver:

- active-character and round tracking;
- cross-round opponent memory;
- lineup manager and next-character strategic conditioning;
- full three-character episode schema and evaluation.

Exit evidence:

- system completes full lineup matches;
- compare persistent opponent memory against reset-every-round behavior;
- all three character policies remain independently evaluable.

## Capability 9 — Human training partner

Deliver:

- difficulty, reaction-delay, aggression, risk, and execution-noise conditioning;
- style presets and optional player-specific adaptation;
- human-readable post-match analysis;
- consent and session controls.

Exit evidence:

- difficulty changes are measurable, not cosmetic;
- reaction time and execution accuracy remain within configured bounds;
- users can stop, inspect, and delete local session data;
- no mode depends on hidden information or anti-cheat evasion.
