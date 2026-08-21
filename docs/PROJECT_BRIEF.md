# Project Brief

## Objective

Build a serious, screen-only research platform that can eventually support `taka_sasuke`,
`white_mask`, and `pain` in training mode, game-provided AI practice, and private matches with
consenting friends. Shared temporal combat knowledge must remain separate from character-specific
perception templates, calibrated capabilities, timings, adapters, and policy heads.

The immediate product is not an autonomous fighter. It is a safe, evidence-preserving platform for
capture, passive state estimation, structured observation views, semantic decisions, evaluation,
and later separately authorized learning.

## Research questions

- Can visible pixels support useful, confidence-calibrated temporal combat state?
- Does SQ, which knows self identity but hides opponent identity, generalize better than IR while
  retaining useful character conditioning?
- Does a shared temporal backbone plus small character adapters outperform separate full stacks?
- Do factorized semantic actions and explicit capability masks improve legality and auditability?
- Can behavior style be evaluated independently from competence and runtime safety?

## Final system shape

The approved runtime is:

```text
screen capture -> perception estimates -> TemporalCombatState -> IR/SQ/IQ
-> shared temporal backbone -> character conditioning -> factorized SemanticAction
-> ActionCapabilities -> adapter -> scheduler -> SafetyGate -> input
```

Recording, registries, and evaluation remain side systems. Learning consumes immutable derived
datasets and produces versioned candidates. World models and league methods remain experimental and
outside the runtime architecture.

## Current verified product

The repository has a mock-verified Foundation runtime/recording spine and synthetic-tested V2
contracts. It does not have passive game perception, calibrated mechanics, a trained policy, a live
gameplay runner, or verified native input/capture evidence.

## Success criteria

Progress is accepted only when the relevant artifact and failure path are tested and documented.
Simulation, schema, or contract evidence must not be described as native emulator, policy quality,
or gameplay evidence. Real input remains a separate Product Owner and safety gate.

## Non-goals and forbidden shortcuts

- ranked/public matchmaking or non-consenting opponents;
- game memory, injection, hooks, packets, hidden state, or anti-cheat bypass;
- automatically scraping copyrighted videos;
- fabricated mechanics, labels, perception, users, matches, or results;
- one monolithic script or one full stack per character;
- policy output that knows key bindings or bypasses scheduler/safety;
- beginning BC, RL, self-play, HELT/PFSP, or a world model without a new authorized work order.
