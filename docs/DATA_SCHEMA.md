# Data Schema

## Principles

1. Raw data is immutable.
2. Every event uses a monotonic nanosecond timestamp within a session.
3. Human-readable metadata also stores UTC time.
4. Raw, processed, and training-set layers are separate.
5. Every derived artifact records source episode IDs, code commit, configuration hash, and processing version.
6. Real, pseudo-labeled, and imagined transitions are never mixed without provenance.

## Storage layout

```text
datasets/
├── raw/
│   ├── demonstrations/
│   ├── agent_runs/
│   └── imported_videos/
├── processed/
│   ├── perception_v1/
│   ├── pseudo_actions_v1/
│   └── latent_features_v1/
└── training_sets/
    └── <dataset_version>/
```

The repository ignores all dataset contents by default.

## Episode directory

```text
<episode_id>/
├── manifest.json
├── video.mp4
├── frame_index.jsonl
├── input_events.jsonl
├── actions.jsonl
├── optional_annotations.jsonl
├── optional_policy_events.jsonl
└── optional_summary.json
```

## Episode manifest

Required fields:

- `schema_version`;
- `episode_id`;
- `session_id`;
- `source_type`: human demonstration, scripted agent, learned agent, or imported video;
- `started_at_utc` and `ended_at_utc`;
- `started_monotonic_ns` and `ended_monotonic_ns`;
- `controlled_character`;
- `lineup` and optional round boundaries;
- `emulator_profile_id`;
- `capture_config_hash`;
- `control_config_hash`;
- `character_config_hash`;
- `code_commit`;
- `model_version`, if applicable;
- filenames and checksums;
- quality flags;
- free-form notes.

## Frame index event

```json
{
  "schema_version": 1,
  "frame_id": 12345,
  "timestamp_ns": 817234900000,
  "video_pts": 44100,
  "duplicate": false,
  "dropped_before": 0
}
```

## Raw input event

```json
{
  "schema_version": 1,
  "timestamp_ns": 817234912345,
  "device": "keyboard",
  "key": "K",
  "event_type": "down",
  "source": "human"
}
```

## Derived action event

A derived action represents the full control state, not only button edges.

```json
{
  "schema_version": 1,
  "start_ns": 817234912345,
  "end_ns": 817235042345,
  "movement": "up_right",
  "button": "skill_1",
  "character_id": "taka_sasuke",
  "source": "human",
  "confidence": 1.0
}
```

## Perception event

Every field that may be uncertain has a confidence value or an explicit unknown state.

```json
{
  "schema_version": 1,
  "timestamp_ns": 817235000000,
  "self_position": {"x": 0.32, "y": 0.71},
  "opponent_position": {"x": 0.68, "y": 0.65},
  "self_health": 0.84,
  "opponent_health": 0.61,
  "active_character": "taka_sasuke",
  "self_animation": "attacking",
  "opponent_animation": "moving",
  "round_phase": "active",
  "confidence": {
    "positions": 0.87,
    "health": 0.96,
    "active_character": 0.99
  }
}
```

## Episode transition

Training transitions may reference raw frames rather than duplicate images.

Required provenance:

- source episode and frame range;
- real, pseudo-labeled, or imagined;
- observation version;
- action-label version;
- reward version;
- terminal and truncation reason;
- confidence and quality flags.

## Dataset split policy

- Split by episode or session, never randomly by frame.
- Keep all frames from one match in the same split.
- Maintain a fixed holdout containing different sessions and opponent conditions.
- Track per-character and cross-character distribution.
- Imported videos must not leak near-duplicate clips across splits.

## Retention and privacy

- Raw data remains local unless the user explicitly exports it.
- Do not record unrelated desktop regions.
- Provide future tooling to redact names, notifications, and account identifiers.
- Imported content must be user-supplied or legally usable.
