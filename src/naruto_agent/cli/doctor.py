from __future__ import annotations

import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import psutil
import typer
from rich.console import Console
from rich.table import Table

from naruto_agent.runtime.window import WindowsWindowLocator

app = typer.Typer(add_completion=False, help="Inspect the local project environment safely.")
console = Console()


def _module_status(name: str) -> str:
    return "available" if importlib.util.find_spec(name) is not None else "missing"


def _gpu_report() -> str:
    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi is None:
        return "not visible (nvidia-smi not found)"
    try:
        result = subprocess.run(
            [
                nvidia_smi,
                "--query-gpu=name,driver_version,memory.total",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return f"nvidia-smi found but query failed: {type(exc).__name__}: {exc}"
    visible = "; ".join(line.strip() for line in result.stdout.splitlines() if line.strip())
    return visible or "nvidia-smi returned no visible GPU"


def _torch_report() -> str:
    if importlib.util.find_spec("torch") is None:
        return "missing (optional in Foundation)"
    try:
        import torch

        return f"{torch.__version__}; CUDA available={torch.cuda.is_available()}"
    except Exception as exc:
        return f"installed but inspection failed: {type(exc).__name__}: {exc}"


def _windows_report() -> tuple[str, list[dict[str, Any]]]:
    if sys.platform != "win32":
        return "not available on this platform", []
    try:
        windows = [
            {
                "handle": item.handle,
                "title": item.title,
                "process_name": item.process_name,
                "width": item.width,
                "height": item.height,
            }
            for item in WindowsWindowLocator().enumerate()
            if item.visible and item.title and item.width >= 640 and item.height >= 360
        ]
    except Exception as exc:
        return f"enumeration failed: {type(exc).__name__}: {exc}", []
    return f"{len(windows)} visible top-level candidates (minimum 640x360)", windows


def collect_report(project_root: Path) -> tuple[dict[str, str], list[dict[str, Any]], list[str]]:
    windows_summary, windows = _windows_report()
    report: dict[str, str] = {
        "OS": platform.platform(),
        "Windows build": platform.version() if sys.platform == "win32" else "not Windows",
        "Native Windows": str(sys.platform == "win32"),
        "WSL detected": str(
            "microsoft" in platform.release().lower() or "WSL_DISTRO_NAME" in os.environ
        ),
        "Python": sys.version.replace("\n", " "),
        "Python executable": sys.executable,
        "Monotonic clock": (
            f"{time.get_clock_info('perf_counter').implementation}; "
            f"resolution={time.get_clock_info('perf_counter').resolution:.9f}s"
        ),
        "CPU logical cores": str(psutil.cpu_count(logical=True)),
        "RAM total GiB": f"{psutil.virtual_memory().total / (1024**3):.2f}",
        "GPU": _gpu_report(),
        "Git": shutil.which("git") or "not found",
        "DXCam": _module_status("dxcam"),
        "pywin32": _module_status("win32gui"),
        "pynput": _module_status("pynput"),
        "OpenCV": _module_status("cv2"),
        "PyTorch/CUDA": _torch_report(),
        "Capture backends": f"mock=available, dxcam={_module_status('dxcam')}",
        "Input backends": (
            "dry-run=available, mock=available, "
            f"SendInput={'available' if sys.platform == 'win32' else 'unavailable'}"
        ),
        "Window candidates": windows_summary,
    }
    messages: list[str] = []
    version = sys.version_info[:2]
    if version not in {(3, 11), (3, 12)}:
        messages.append("Use Python 3.11 or 3.12; the current interpreter is unsupported.")
    if sys.platform == "win32" and _module_status("dxcam") == "missing":
        messages.append("Install the windows extra to benchmark Desktop Duplication capture.")
    if sys.platform == "win32" and _module_status("pynput") == "missing":
        messages.append("Install the windows extra before enabling the emergency-stop listener.")
    for relative in ("configs/local", "datasets", "artifacts"):
        path = project_root / relative
        try:
            path.mkdir(parents=True, exist_ok=True)
            writable = os.access(path, os.W_OK)
        except OSError as exc:
            writable = False
            messages.append(f"Cannot prepare {relative}: {type(exc).__name__}: {exc}")
        report[f"Writable: {relative}"] = str(writable)
        if not writable:
            messages.append(f"Make {path} writable before using local runtime tools.")
    if not windows:
        messages.append("No emulator candidate is currently visible; open it before calibration.")
    return report, windows, messages


@app.command()
def main(
    project_root: Path | None = typer.Option(None, exists=True, file_okay=False),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Print a safe environment report. It never captures frames or sends input."""

    report, windows, messages = collect_report(project_root or Path.cwd())
    if json_output:
        console.print_json(json.dumps({"checks": report, "windows": windows, "messages": messages}))
        return

    table = Table(title="Naruto Agent Lab — Foundation Doctor")
    table.add_column("Check")
    table.add_column("Result")
    for key, value in report.items():
        table.add_row(key, value)
    console.print(table)
    if windows:
        window_table = Table("Handle", "Process", "Title", "Size")
        for item in windows:
            window_table.add_row(
                str(item["handle"]),
                str(item["process_name"] or "unknown"),
                str(item["title"]),
                f"{item['width']}x{item['height']}",
            )
        console.print(window_table)
    for message in messages:
        console.print(f"[yellow]Action: {message}[/yellow]")


if __name__ == "__main__":
    app()
