"""Command-line interface entrypoint for the Raylings learning framework."""

from pathlib import Path

import typer
from rich.table import Table

from raylings import __version__
from raylings.daemon import RayDaemon
from raylings.manifest import get_exercise_by_name, get_manifest
from raylings.models import Exercise
from raylings.runner import ExerciseRunner
from raylings.ui import (
    console,
    render_banner,
    render_cluster_status,
    render_hint,
    render_progress,
    render_result,
)
from raylings.watcher import ExerciseWatcher

app = typer.Typer(
    name="raylings",
    help="Interactive Ray learning CLI inspired by Rustlings.",
    no_args_is_help=True,
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    """Callback for --version CLI option."""
    if value:
        render_banner()
        console.print(
            f"[bold cyan]raylings[/bold cyan] version [bold green]{__version__}[/bold green]\n"
        )
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show raylings version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Raylings CLI main entrypoint callback."""


@app.command(name="version")
def version_command() -> None:
    """Display raylings branding banner and current version."""
    render_banner()
    console.print(
        f"[bold cyan]raylings[/bold cyan] version [bold green]{__version__}[/bold green]\n"
    )


@app.command(name="init")
def init_command(
    target_dir: Path = typer.Option(
        Path("."),
        "--directory",
        "-d",
        help="Target directory to initialize raylings exercises in (defaults to current working directory)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing exercise files if they already exist",
    ),
) -> None:
    """Initialize a fresh Raylings workspace by extracting bundled exercises."""
    import importlib.resources
    import shutil

    render_banner()
    exercises_dest = target_dir / "exercises"

    if exercises_dest.exists() and not force:
        console.print(
            f"[bold yellow]Directory '{exercises_dest}' already exists.[/bold yellow]\n"
            "Use [bold cyan]raylings init --force[/bold cyan] to overwrite, or run [bold green]raylings watch[/bold green] to continue learning."
        )
        raise typer.Exit(0)

    try:
        bundled_pkg = importlib.resources.files("raylings")
        bundled_exercises = bundled_pkg / "exercises"

        if hasattr(bundled_exercises, "is_dir") and bundled_exercises.is_dir():
            if exercises_dest.exists() and force:
                shutil.rmtree(exercises_dest)
            shutil.copytree(str(bundled_exercises), str(exercises_dest))
        else:
            # Fallback to local source tree if running in editable dev mode
            repo_exercises = Path(__file__).parent.parent.parent / "exercises"
            if repo_exercises.exists():
                if exercises_dest.exists() and force:
                    shutil.rmtree(exercises_dest)
                shutil.copytree(str(repo_exercises), str(exercises_dest))
            else:
                console.print(
                    "[bold red]Failed to locate bundled exercises in raylings package.[/bold red]"
                )
                raise typer.Exit(1)

        console.print(
            f"[bold green]✨ Raylings workspace initialized successfully in [white]{target_dir.resolve()}[/white]![/bold green]\n\n"
            "To begin your Ray learning journey, run:\n"
            "  [bold cyan]raylings watch[/bold cyan]\n"
        )
    except Exception as e:
        console.print(f"[bold red]Error initializing workspace:[/bold red] {e}")
        raise typer.Exit(1)


@app.command(name="list")
def list_command() -> None:
    """List all 14 curriculum chapters and exercises with status breakdown."""
    render_banner()
    manifest = get_manifest()
    runner = ExerciseRunner()

    completed_count = 0
    for ex in manifest.all_exercises:
        if ex.file_path.exists() and not runner.check_marker(ex.file_path):
            res = runner.run_exercise(ex, timeout=10.0)
            if res.passed:
                completed_count += 1

    render_progress(manifest, completed_count=completed_count)


@app.command(name="run")
def run_command(
    exercise_name: str = typer.Argument(
        ...,
        help="Exercise name (e.g. basics01) or direct file path to execute",
    ),
    timeout: float = typer.Option(
        30.0,
        "--timeout",
        "-t",
        help="Subprocess timeout in seconds",
    ),
) -> None:
    """Run an exercise or solution once and display evaluation diagnostics."""
    ex = get_exercise_by_name(exercise_name)
    if ex is None:
        target_path = Path(exercise_name)
        if target_path.exists():
            ex = Exercise(
                name=target_path.stem,
                title=target_path.stem,
                path=str(target_path),
                chapter_name=target_path.parent.name,
            )
        else:
            console.print(f"[bold red]Exercise '{exercise_name}' not found.[/bold red]")
            raise typer.Exit(1)

    runner = ExerciseRunner()
    res = runner.run_exercise(ex, timeout=timeout)
    render_result(res)
    if not res.passed:
        raise typer.Exit(1)


@app.command(name="hint")
def hint_command(
    exercise_name: str = typer.Argument(
        "",
        help="Name of exercise (e.g. basics01). Defaults to current incomplete exercise.",
    ),
    level: int = typer.Option(
        0,
        "--level",
        "-l",
        help="Progressive hint level index (0-indexed)",
    ),
) -> None:
    """Display progressive hints for an exercise."""
    target_ex: Exercise | None = None
    if not exercise_name:
        watcher = ExerciseWatcher()
        target_ex = watcher.find_current_exercise()
        if target_ex is None:
            console.print("[yellow]No incomplete exercises found in curriculum.[/yellow]")
            raise typer.Exit(0)
    else:
        target_ex = get_exercise_by_name(exercise_name)

    if target_ex is None:
        console.print(f"[bold red]Exercise '{exercise_name}' not found.[/bold red]")
        raise typer.Exit(1)

    render_hint(target_ex, hint_level=level)


@app.command(name="test")
def test_command(
    exercise_name: str = typer.Argument(
        "",
        help="Optional specific exercise name to test solution for",
    ),
    all_solutions: bool = typer.Option(
        True,
        "--all",
        help="Execute all canonical reference solutions",
    ),
) -> None:
    """Execute canonical reference solutions and verify correctness."""
    render_banner()
    runner = ExerciseRunner()
    manifest = get_manifest()

    if exercise_name:
        ex = get_exercise_by_name(exercise_name)
        if ex is None:
            console.print(f"[bold red]Exercise '{exercise_name}' not found.[/bold red]")
            raise typer.Exit(1)
        res = runner.run_solution(ex)
        render_result(res)
        if not res.passed:
            raise typer.Exit(1)
        return

    exercises = manifest.all_exercises
    if not exercises:
        console.print("[yellow]No exercises found in curriculum manifest.[/yellow]")
        return

    passed_count = 0
    failed_count = 0
    console.print(f"[bold cyan]Testing {len(exercises)} reference solutions...[/bold cyan]\n")

    table = Table(
        title="Solution Verification Summary",
        border_style="dim",
        header_style="bold magenta",
    )
    table.add_column("Exercise", style="bold cyan", width=16)
    table.add_column("Solution Path", style="dim white")
    table.add_column("Result", justify="center", width=10)

    for ex in exercises:
        res = runner.run_solution(ex)
        if res.passed:
            passed_count += 1
            table.add_row(ex.name, str(ex.solution_path), "[bold green]PASS[/bold green]")
        else:
            failed_count += 1
            table.add_row(ex.name, str(ex.solution_path), "[bold red]FAIL[/bold red]")

    console.print(table)
    console.print(
        f"\n[bold]Summary:[/bold] [bold green]{passed_count} passed[/bold green], "
        f"[bold red]{failed_count} failed[/bold red]\n"
    )

    if failed_count > 0:
        raise typer.Exit(1)


@app.command(name="daemon")
def daemon_command(
    action: str = typer.Argument(
        "status",
        help="Action to perform: start | stop | status | restart",
    ),
) -> None:
    """Manage the background Python Ray session daemon."""
    daemon = RayDaemon()
    action_lower = action.lower()

    if action_lower == "status":
        info = daemon.get_cluster_info()
        render_cluster_status(info)
    elif action_lower == "start":
        console.print("[cyan]Starting Ray daemon session...[/cyan]")
        daemon.start()
        info = daemon.get_cluster_info()
        render_cluster_status(info)
    elif action_lower == "stop":
        console.print("[yellow]Stopping Ray daemon session...[/yellow]")
        daemon.stop()
        console.print("[green]Ray daemon stopped successfully.[/green]")
    elif action_lower == "restart":
        console.print("[cyan]Restarting Ray daemon session...[/cyan]")
        daemon.stop()
        daemon.start()
        info = daemon.get_cluster_info()
        render_cluster_status(info)
    else:
        console.print(
            f"[bold red]Unknown daemon action: '{action}'. "
            "Supported actions: start, stop, status, restart.[/bold red]"
        )
        raise typer.Exit(1)


@app.command(name="watch")
def watch_command(
    ctx: typer.Context,
    warm_daemon: bool = typer.Option(
        True,
        "--warm-daemon/--no-warm-daemon",
        help="Pre-warm Ray daemon session before watching",
    ),
    exercise_dir: Path = typer.Option(
        Path("exercises"),
        "--dir",
        "-d",
        help="Root directory containing curriculum exercises",
    ),
) -> None:
    """Interactive watcher mode: continuously monitors files and advances upon completion."""
    daemon = RayDaemon() if warm_daemon else None
    watcher = ExerciseWatcher(daemon=daemon)
    watcher.watch_loop(exercise_dir=exercise_dir)


if __name__ == "__main__":
    app()
