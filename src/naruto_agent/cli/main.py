from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from naruto_agent.calibration import build_local_profile, save_local_profile, validate_local_profile
from naruto_agent.config.loader import load_emulator_profile
from naruto_agent.demo import run_mock_vertical_loop
from naruto_agent.runtime.capture.benchmark import run_capture_benchmark
from naruto_agent.runtime.capture.dxcam_backend import DXCamCaptureBackend, WindowCaptureProfile
from naruto_agent.runtime.window import WindowQuery, WindowsWindowLocator

app = typer.Typer(add_completion=False, help="Safe Foundation runtime and recording tools.")
console = Console()


def _parse_assignments(values: list[str], allowed: set[str]) -> dict[str, str | None]:
    parsed: dict[str, str | None] = {name: None for name in allowed}
    for value in values:
        try:
            name, binding = value.split("=", 1)
        except ValueError as exc:
            raise typer.BadParameter(f"expected NAME=VALUE, received {value!r}") from exc
        if name not in allowed or not binding.strip():
            raise typer.BadParameter(
                f"invalid assignment {value!r}; allowed names: {sorted(allowed)}"
            )
        parsed[name] = binding.strip()
    return parsed


def _parse_rectangle(
    value: str | None, *, normalized: bool
) -> tuple[float, float, float, float] | tuple[int, int, int, int] | None:
    if value is None:
        return None
    try:
        parts = tuple(float(item.strip()) for item in value.split(","))
    except ValueError as exc:
        raise typer.BadParameter("rectangle must be left,top,right,bottom") from exc
    if len(parts) != 4:
        raise typer.BadParameter("rectangle must contain exactly four numbers")
    left, top, right, bottom = parts
    if normalized:
        if not all(0.0 <= item <= 1.0 for item in parts) or right <= left or bottom <= top:
            raise typer.BadParameter(
                "normalized region must be within [0,1] and have positive area"
            )
        return parts
    integers = tuple(int(item) for item in parts)
    if any(float(integer) != original for integer, original in zip(integers, parts, strict=True)):
        raise typer.BadParameter("crop values must be whole pixels")
    return integers


@app.command("windows")
def windows(
    title: str | None = typer.Option(None),
    process: str | None = typer.Option(None),
    minimum_width: int = typer.Option(1),
    minimum_height: int = typer.Option(1),
) -> None:
    locator = WindowsWindowLocator()
    matches = locator.find(
        WindowQuery(
            title_substring=title,
            process_name=process,
            minimum_width=minimum_width,
            minimum_height=minimum_height,
        )
    )
    table = Table("Handle", "Process", "Title", "Size")
    for item in matches:
        table.add_row(
            str(item.handle),
            item.process_name or "unknown",
            item.title,
            f"{item.width}x{item.height}",
        )
    console.print(table)


@app.command("calibrate-create")
def calibrate_create(
    profile_id: str,
    output: Path = typer.Option(..., help="New path under configs/local; never overwritten."),
    title: str | None = typer.Option(None),
    process: str | None = typer.Option(None),
    crop: str | None = typer.Option(None, help="Window-relative L,T,R,B pixels."),
    movement_key: list[str] | None = typer.Option(None, help="Repeat NAME=KEY."),
    button_key: list[str] | None = typer.Option(None, help="Repeat NAME=KEY."),
    emergency_stop: str | None = typer.Option(None, help="Normal key such as F12."),
    ui_region: list[str] | None = typer.Option(None, help="Repeat NAME=L,T,R,B normalized."),
) -> None:
    locator = WindowsWindowLocator()
    selected = locator.select(WindowQuery(title_substring=title, process_name=process))
    movement_names = {"up", "down", "left", "right"}
    button_names = {
        "normal_attack",
        "skill_1",
        "skill_2",
        "ultimate",
        "substitution",
        "secret_scroll",
        "summon",
    }
    regions: dict[str, tuple[float, float, float, float] | None] = {}
    for assignment in ui_region or []:
        try:
            name, rectangle = assignment.split("=", 1)
        except ValueError as exc:
            raise typer.BadParameter("UI regions require NAME=L,T,R,B") from exc
        parsed_region = _parse_rectangle(rectangle, normalized=True)
        assert parsed_region is not None
        regions[name] = parsed_region  # type: ignore[assignment]
    parsed_crop = _parse_rectangle(crop, normalized=False)
    profile = build_local_profile(
        profile_id=profile_id,
        window=selected,
        crop_pixels=parsed_crop,  # type: ignore[arg-type]
        movement=_parse_assignments(movement_key or [], movement_names),
        buttons=_parse_assignments(button_key or [], button_names),
        emergency_stop=emergency_stop,
        ui_regions=regions,
        verified=False,
    )
    path = save_local_profile(profile, output)
    console.print(f"Created unverified local profile: {path}")
    console.print("Edit crop, normalized UI regions, and keys; validate before any live opt-in.")


@app.command("calibrate-validate")
def calibrate_validate(path: Path, live_ready: bool = typer.Option(False)) -> None:
    profile = validate_local_profile(path, require_live_ready=live_ready)
    console.print(f"Valid profile {profile.profile_id} version {profile.profile_version}")
    console.print(f"Verified for live input: {profile.verified}")


@app.command("capture-benchmark")
def capture_benchmark(
    profile_path: Path,
    frames: int = typer.Option(300, min=1),
    sample: Path | None = typer.Option(None, help="Explicit optional .npy sample destination."),
) -> None:
    profile = load_emulator_profile(profile_path)
    locator = WindowsWindowLocator()
    selected = locator.select(
        WindowQuery(
            title_substring=profile.window.title_contains,
            process_name=profile.window.process_name,
            minimum_width=profile.window.minimum_width,
            minimum_height=profile.window.minimum_height,
        )
    )
    backend = DXCamCaptureBackend(
        WindowCaptureProfile(
            window=selected,
            crop_pixels=profile.capture.crop_pixels,
            target_fps=profile.capture.target_fps,
            queue_size=profile.capture.queue_size,
            frozen_frame_threshold=profile.capture.frozen_frame_threshold,
        )
    )
    report = run_capture_benchmark(backend, frame_limit=frames, sample_path=sample)
    console.print_json(json.dumps(report.as_dict()))


@app.command("mock-demo")
def mock_demo(
    output_root: Path | None = typer.Option(None),
    frames: int = typer.Option(6, min=1),
) -> None:
    episode = run_mock_vertical_loop(output_root=output_root, frame_count=frames)
    console.print(f"Valid dry-run episode: {episode}")
