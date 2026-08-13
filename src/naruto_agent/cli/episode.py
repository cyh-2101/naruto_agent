from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from naruto_agent.data.recorder import inspect_episode, recover_episode, validate_episode

app = typer.Typer(add_completion=False, help="Validate and inspect recorded episodes safely.")
console = Console()


@app.command("validate")
def validate(path: Path = typer.Argument(..., exists=True, file_okay=False)) -> None:
    errors = validate_episode(path)
    if errors:
        for error in errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)
    console.print("Episode is valid.")


@app.command("inspect")
def inspect(path: Path = typer.Argument(..., exists=True, file_okay=False)) -> None:
    console.print_json(json.dumps(inspect_episode(path)))


@app.command("recover")
def recover(
    path: Path = typer.Argument(..., exists=True, file_okay=False),
    reason: str = typer.Option(..., help="Human-readable crash/recovery reason."),
) -> None:
    manifest = recover_episode(path, reason=reason)
    console.print(f"Recovered episode {manifest.episode_id}; validation is still required.")
