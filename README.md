# Naruto Agent Lab

Naruto Agent Lab is a screen-only, multi-character fighting-agent research platform for
`taka_sasuke`, `white_mask`, and `pain`. It is designed around the final modular architecture:
runtime I/O, perception, belief, skills, policies, learning, data, and evaluation remain separate,
and shared combat knowledge remains distinct from character-specific packages.

The current Foundation slice does **not** contain game perception, learned control, character
mechanics, reinforcement learning, self-play, or a live gameplay runner. All character mechanics
and timings remain explicitly unverified.

## Safety boundary

Use is limited to training mode, game-provided AI practice, and private matches with consenting
friends. Ranked/public automation, play against non-consenting people, memory access, injection,
packet manipulation, hidden-state extraction, anti-cheat bypass, and automatic video scraping are
forbidden.

Input is dry-run by default. The native Windows input backend cannot be constructed without an
explicit live opt-in, a verified local profile, a uniquely selected and focused window, a running
emergency-stop listener, and a visible live-session indicator. Policies communicate only through
`ControlCommand`, the action scheduler, and the safety gate.

## Implemented Foundation components

- strict typed contracts and validated base, character, and emulator configuration;
- native Win32 top-level window discovery with title/process/visibility/size filtering and explicit
  ambiguity errors;
- bounded DXCam/Desktop Duplication backend with monotonic timestamps, duplicate/freeze detection,
  clean shutdown, optional explicit sample export, and benchmark metrics;
- dry-run, mock, and Win32 `SendInput` backends with held-key cleanup and emergency-stop support;
- versioned local calibration profiles under ignored `configs/local/`;
- crash-tolerant episode manifests, frame/input/control indexes, checksums, quality flags, inspection,
  recovery, and a bounded immutable NumPy-frame fallback;
- a non-Windows-safe mock vertical loop from placeholder observation through neutral policy output,
  safety scheduling, mock input, and recording;
- native diagnostics and 40 safe automated tests.

## Quick start

Use Python 3.11 or 3.12. On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/doctor.py --project-root .
python -m pytest -ra
python -m ruff check .
python -m mypy src/naruto_agent
python scripts/runtime.py mock-demo --frames 8
```

If `python` is not already Python 3.11/3.12, pass its full path to the bootstrap script:

```powershell
.\scripts\bootstrap.ps1 -PythonExecutable "C:\Path\To\Python312\python.exe"
```

Native runtime packages are separate so the safe mock suite stays portable:

```powershell
python -m pip install -e ".[dev,windows]"
python scripts/doctor.py --project-root .
```

Do not proceed to live input from those commands. See [the runbook](docs/RUNBOOK.md) for calibration,
capture benchmarking, episode validation, and the remaining native verification gates.

项目负责人可在每个 Stage 完成后使用 [learners.md](learners.md) 让 ChatGPT 按当前已验证能力进行教学。

## Verified status

On 2026-08-13, Python 3.12.13 passed all 40 safe tests and bytecode compilation. The mock demo
produced an eight-frame, eight-control-interval episode that passed checksum, schema, finalization,
and timestamp validation. The native doctor ran on Windows 11 build 26200 and found writable local
paths, a high-resolution QueryPerformanceCounter clock, 32 logical CPU cores, 15.22 GiB RAM, and an
NVIDIA GPU visible through `nvidia-smi`.

DXCam, pynput, a real emulator window, production capture performance, the emergency-stop hotkey,
and `SendInput` were not exercised in that run. Ruff passed; mypy was not executable because its
package download repeatedly timed out. This limitation is recorded in
`docs/EXPERIMENT_LOG.md`. The directory was also not a Git worktree, so no commit ID or Git status
could be recorded.
