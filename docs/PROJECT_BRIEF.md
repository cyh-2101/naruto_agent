# Project Brief

## Working title

Naruto Agent Lab

## Research objective

Build a screen-only multi-character fighting agent that learns from:

1. synchronized human demonstrations containing video and input events;
2. action-free gameplay videos;
3. limited closed-loop interaction with training opponents.

The initial supported characters are:

- `taka_sasuke` — 鹰小队佐助;
- `white_mask` — 白面具;
- `pain` — 佩恩.

The system should share general combat understanding across characters while preserving character-specific mechanics, visual templates, timing, skill graphs, adapters, and policy outputs.

## Core research questions

1. Can action-free gameplay video reduce the amount of real emulator interaction required?
2. Which combat knowledge transfers across characters, and which requires character-specific adapters?
3. Does a hybrid observation composed of structured state plus a learned visual latent outperform either alone?
4. Does hierarchical control improve reliability over direct frame-level key prediction?
5. Can an explicit belief state improve decisions under hidden cooldowns, uncertain intent, and ambiguous animations?
6. Can one conditional policy produce controllable styles and human-like difficulty levels?
7. Can information learned in the first lineup round improve decisions for later characters?

## Product objective

Create a private training partner that can:

- separately control all three supported characters;
- complete a full lineup match;
- adapt to recurring opponent patterns across rounds;
- expose adjustable reaction delay, difficulty, aggression, and execution noise;
- record every episode for inspection and continued learning.

The system is not intended to maximize unfair competitive advantage. It must remain within training/private-consent scope.

## Final capability picture

The final system consists of:

- native Windows capture and input runtime;
- synchronized event recorder and replay viewer;
- structured perception plus a temporal visual encoder;
- recurrent belief state and opponent model;
- hierarchical strategy, tactic, and execution policies;
- character skill packages and conditional adapters;
- behavior cloning, inverse dynamics, latent-action learning, offline RL, and limited online refinement;
- a short-horizon world model for representation learning and imagined rollouts;
- policy registry, historical opponent pool, evaluation harness, and lineup memory;
- style and difficulty conditioning.

## Success criteria

The project succeeds technically when it can demonstrate, with reproducible evidence:

1. stable low-latency capture and safe input control;
2. accurate synchronized recordings;
3. measurable perception quality;
4. reliable closed-loop execution for each character;
5. improved performance from human demonstrations over scripted/random baselines;
6. measurable transfer across the three characters;
7. measurable benefit, or a defensible negative result, from action-free video pretraining;
8. a complete three-character match with persistent opponent context;
9. controllable style and difficulty without hidden information or machine-perfect reaction.

## Non-goals

- full support for every character at the beginning;
- client modification or hidden-state access;
- ranked automation;
- claiming self-play before both sides are actually controllable;
- reproducing a proprietary internal game simulator;
- building an impressive UI before the learning and evaluation foundations work.
