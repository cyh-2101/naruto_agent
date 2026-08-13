# Architectural Decisions

Use one entry per durable decision. Do not silently rewrite history; mark entries superseded when
needed.

## ADR-001 — Screen-only observation and normal emulator input

- Status: accepted
- Decision: The agent receives only pixels visible in the calibrated emulator window and acts
  through ordinary emulator key mappings.
- Reason: Keeps the research question aligned with human-visible information and avoids hidden-state
  dependence.
- Rejected: game-memory access, process injection, and packet manipulation.

## ADR-002 — Final architecture first, capability slices second

- Status: accepted
- Decision: Early work implements thin, tested slices inside the final modular architecture rather
  than a disposable end-to-end toy.
- Reason: Runtime, data, and contracts should survive later model changes.

## ADR-003 — Shared combat brain with character-specific adapters and skill packages

- Status: accepted
- Decision: General perception, belief, and strategy are shared; mechanics and execution remain
  character-specific.
- Reason: Enables transfer while avoiding false assumptions that all characters behave identically.

## ADR-004 — Hybrid structured state plus learned temporal visual latent

- Status: accepted
- Decision: Policies consume interpretable estimates and a learned frame-sequence embedding.
- Reason: Structured state improves debugging; latent features preserve information that manual
  parsers miss.

## ADR-005 — Hierarchical decisions and mandatory action scheduler

- Status: accepted
- Decision: Separate strategic intent, tactical macro action, and low-level timed execution. No
  policy sends keys directly.
- Reason: Reduces action-space complexity and centralizes safety, timing, and legal transitions.

## ADR-006 — Demonstrations before online reinforcement learning

- Status: accepted
- Decision: Start learned control from synchronized human demonstrations; use online interaction
  later for closed-loop correction.
- Reason: Emulator interaction is slow, and random raw-pixel exploration is inefficient.

## ADR-007 — Raw data is immutable and provenance is mandatory

- Status: accepted
- Decision: Preserve raw videos and events, regenerate processed layers, and label real,
  pseudo-labeled, and imagined data separately.
- Reason: Future perception and labeling versions must be able to reprocess old episodes.

## ADR-008 — Python 3.11/3.12 project environment

- Status: accepted
- Decision: Use a dedicated Python 3.11 or 3.12 environment for compatibility and reproducibility.
- Reason: Decouples the project from the user's system Python and reduces ML/runtime package risk.

## ADR-009 — Documented Win32 APIs and optional DXCam for native runtime I/O

- Status: accepted
- Decision: Enumerate and verify focus through documented `user32` APIs, send normal keys through
  `SendInput`, and capture the calibrated desktop region through optional DXCam/Desktop Duplication.
  Emulator selection remains configuration-driven rather than brand-specific.
- Reason: These backends preserve the screen-only boundary, support native low-latency operation,
  and can be absent without breaking mocks or non-Windows tests.
- Rejected: repeated ADB PNG capture, emulator-brand hard-coding, game hooks, injection, and hidden
  state access.

## ADR-010 — Explicit ambiguity is safer than heuristic window selection

- Status: accepted
- Decision: Window matches are deterministically sorted, but selection succeeds only for exactly one
  result. Multiple matches raise an error listing every candidate.
- Reason: Silently choosing a plausible window could capture unrelated desktop content or direct
  input to the wrong application.
- Rejected: first-match selection and largest-window heuristics.

## ADR-011 — High-resolution monotonic runtime clock

- Status: accepted
- Decision: Runtime-generated timestamps use `time.perf_counter_ns()`, which is monotonic and maps to
  `QueryPerformanceCounter` in the verified Windows environment. UTC remains separate manifest
  metadata.
- Reason: The available interpreter's `time.monotonic()` used a much coarser Windows clock, while
  frame/input synchronization and latency measurement need a high-resolution monotonic source.
- Rejected: wall-clock synchronization and mixing unrelated runtime clock epochs.

## ADR-012 — Dry-run factory plus scheduler-enforced live boundary

- Status: accepted
- Decision: Input construction defaults to `DryRunInputBackend`. A live backend requires explicit
  opt-in, a verified profile, a selected focused window, valid normal-key bindings, a successfully
  started emergency-stop listener, and a visible session-indicator callback. Policy commands still
  pass through rate limiting and `SafetyGate` before the backend, which rechecks focus per batch.
- Reason: Defense in depth prevents a caller or stale scheduler snapshot from accidentally sending
  real input.
- Rejected: environment-variable activation, import-time initialization, policy-to-key calls, and
  tests that patch a real backend.

## ADR-013 — Bounded immutable NumPy frames as the Foundation recording fallback

- Status: accepted
- Decision: Until an encoded-video backend is verified, episodes store a configured maximum number
  of immutable `.npy` frames with JSONL indexes, atomic manifests, per-file SHA-256 checksums, and
  explicit `raw_frame_fallback` quality provenance.
- Reason: This narrow fallback is portable, testable without codecs, crash-recoverable, and cannot
  grow without a configured bound.
- Rejected: an unbounded image directory, silently overwriting frames, or claiming video encoding
  before it exists.

## ADR-014 — Local calibration is versioned, ignored, and never overwrites examples

- Status: accepted
- Decision: Real profiles live only under `configs/local/`, start unverified, carry an explicit
  profile version, use normalized UI regions, and are created with exclusive-write semantics.
- Reason: Calibration is machine-specific and potentially privacy-sensitive; example profiles must
  remain reproducible and mechanics must not be inferred from placeholders.
- Rejected: committing personal profiles, modifying `emulator.example.yaml`, and auto-marking a CLI
  generated profile as verified.
