"""Command-line interface entrypoint for the Raylings learning framework."""

import os
import platform
import sys
from pathlib import Path
from typing import Any

import typer
from rich.table import Table

from raylings import __version__
from raylings.daemon import RayDaemon
from raylings.manifest import get_exercise_by_name, get_manifest
from raylings.models import Exercise
from raylings.runner import ExerciseRunner
from raylings.state import get_state_tracker
from raylings.tour import get_tour_engine
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
def list_command(
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output full curriculum metadata and completion status as JSON",
    ),
) -> None:
    """List all 14 curriculum chapters and exercises with status breakdown."""
    manifest = get_manifest()
    runner = ExerciseRunner()

    tracker = get_state_tracker()
    completed_set = tracker.get_completed_set()

    if as_json:
        import json

        chapters_data = []
        for ch in manifest.chapters:
            ex_data = []
            for ex in ch.exercises:
                has_marker = runner.check_marker(ex.file_path) if ex.file_path.exists() else False
                completed = ex.name in completed_set
                ex_data.append(
                    {
                        "name": ex.name,
                        "title": ex.title,
                        "path": ex.path,
                        "chapter_name": ex.chapter_name,
                        "chapter_number": ch.number,
                        "hints": ex.hints,
                        "requires_cluster": ex.requires_cluster,
                        "completed": completed,
                        "has_marker": has_marker,
                        "exists": ex.file_path.exists(),
                    }
                )
            chapters_data.append(
                {
                    "number": ch.number,
                    "name": ch.name,
                    "title": ch.title,
                    "description": ch.description,
                    "exercises": ex_data,
                }
            )
        print(
            json.dumps(
                {
                    "version": __version__,
                    "total_exercises": len(manifest.all_exercises),
                    "chapters": chapters_data,
                },
                indent=2,
            )
        )
        return

    render_banner()
    completed_count = len(completed_set.intersection({ex.name for ex in manifest.all_exercises}))
    render_progress(manifest, completed_count=completed_count)


@app.command(name="progress")
def progress_command(
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output overall progress summary as JSON",
    ),
) -> None:
    """Display overall progress summary and current active exercise."""
    manifest = get_manifest()
    watcher = ExerciseWatcher()
    current_ex = watcher.find_current_exercise()
    tracker = get_state_tracker()
    completed_set = tracker.get_completed_set()

    completed_count = len(completed_set.intersection({ex.name for ex in manifest.all_exercises}))
    total = len(manifest.all_exercises)
    percentage = (completed_count / total * 100.0) if total > 0 else 0.0

    if as_json:
        import json

        print(
            json.dumps(
                {
                    "total": total,
                    "completed": completed_count,
                    "percentage": round(percentage, 1),
                    "current_exercise": current_ex.name if current_ex else None,
                    "current_path": current_ex.path if current_ex else None,
                    "is_finished": current_ex is None,
                },
                indent=2,
            )
        )
        return

    render_banner()
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
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output evaluation result as JSON",
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
            if as_json:
                import json

                print(
                    json.dumps(
                        {
                            "error": f"Exercise '{exercise_name}' not found.",
                            "passed": False,
                        },
                        indent=2,
                    )
                )
                raise typer.Exit(1)
            console.print(f"[bold red]Exercise '{exercise_name}' not found.[/bold red]")
            raise typer.Exit(1)

    runner = ExerciseRunner()
    res = runner.run_exercise(ex, timeout=timeout)
    get_state_tracker().mark_completed(ex.name, res.passed)

    if as_json:
        import json

        print(
            json.dumps(
                {
                    "name": ex.name,
                    "title": ex.title,
                    "path": ex.path,
                    "passed": res.passed,
                    "has_not_done_marker": res.has_not_done_marker,
                    "exit_code": res.exit_code,
                    "output": res.output,
                    "error": res.error,
                },
                indent=2,
            )
        )
        if not res.passed:
            raise typer.Exit(1)
        return

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
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output hints as JSON",
    ),
) -> None:
    """Display progressive hints for an exercise."""
    target_ex: Exercise | None = None
    if not exercise_name:
        watcher = ExerciseWatcher()
        target_ex = watcher.find_current_exercise()
        if target_ex is None:
            if as_json:
                import json

                print(
                    json.dumps(
                        {
                            "message": "No incomplete exercises found in curriculum.",
                            "hints": [],
                        },
                        indent=2,
                    )
                )
                raise typer.Exit(0)
            console.print("[yellow]No incomplete exercises found in curriculum.[/yellow]")
            raise typer.Exit(0)
    else:
        target_ex = get_exercise_by_name(exercise_name)

    if target_ex is None:
        if as_json:
            import json

            print(
                json.dumps(
                    {
                        "error": f"Exercise '{exercise_name}' not found.",
                        "hints": [],
                    },
                    indent=2,
                )
            )
            raise typer.Exit(1)
        console.print(f"[bold red]Exercise '{exercise_name}' not found.[/bold red]")
        raise typer.Exit(1)

    if as_json:
        import json

        sel_hint = (
            target_ex.hints[min(level, len(target_ex.hints) - 1)]
            if target_ex.hints
            else "No hints available for this exercise."
        )
        print(
            json.dumps(
                {
                    "name": target_ex.name,
                    "title": target_ex.title,
                    "hints": target_ex.hints,
                    "selected_level": level,
                    "selected_hint": sel_hint,
                },
                indent=2,
            )
        )
        return

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


@app.command(name="tour")
def tour_command(
    step: int | None = typer.Option(
        None,
        "--step",
        "-s",
        help="Jump directly to a specific 1-indexed tour step (1-5)",
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        "-y",
        help="Run tour non-interactively without waiting for user input",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output tour content and metadata as JSON",
    ),
) -> None:
    """Interactive onboarding tour introducing Raylings and core concepts."""
    engine = get_tour_engine()
    steps = engine.get_steps()

    if as_json:
        import json

        print(json.dumps(engine.to_json_dict(), indent=2))
        return

    if step is not None:
        step_obj = engine.get_step(step)
        if step_obj is None:
            console.print(
                f"[bold red]Invalid step {step}. Please specify a step between 1 and {len(steps)}.[/bold red]"
            )
            raise typer.Exit(1)
        engine.render_step(step_obj)
        return

    is_interactive = (not non_interactive) and sys.stdin.isatty()
    render_banner()

    if not is_interactive:
        for s in steps:
            engine.render_step(s)
            console.print()
        return

    for idx, s in enumerate(steps):
        engine.render_step(s)
        if idx < len(steps) - 1:
            try:
                choice = console.input(
                    "\n[bold cyan]Press Enter for next step (or 'q' to quit)... [/bold cyan]"
                )
            except (EOFError, KeyboardInterrupt):
                console.print("\n[yellow]Tour exited.[/yellow]")
                raise typer.Exit(0)
            if choice.strip().lower() == "q":
                console.print("[yellow]Tour exited.[/yellow]")
                raise typer.Exit(0)
        else:
            console.print(
                "\n[bold green]🎉 Tour complete! Run [cyan]raylings watch[/cyan] to begin your learning journey.[/bold green]\n"
            )


def _get_ram_info() -> str | None:
    """Attempt to detect system physical RAM capacity."""
    try:
        import psutil

        total_gb = psutil.virtual_memory().total / (1024**3)
        return f"{total_gb:.1f} GB"
    except (ImportError, Exception):
        pass

    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        total_gb = (pages * page_size) / (1024**3)
        return f"{total_gb:.1f} GB"
    except (ValueError, AttributeError, OSError):
        return None


def _run_doctor_diagnostics() -> tuple[list[dict[str, Any]], bool]:
    """Execute preflight system and environment diagnostics.

    Returns:
        tuple: (list of diagnostic check dictionaries, has_critical_failure boolean)
    """
    checks: list[dict[str, Any]] = []
    has_critical_failure = False

    # 1. Python version check (>= 3.10 required)
    py_ver = sys.version_info
    py_ver_str = f"{py_ver[0]}.{py_ver[1]}.{py_ver[2]}"
    if py_ver >= (3, 10):
        checks.append(
            {
                "name": "Python Version",
                "status": "pass",
                "critical": True,
                "details": f"Python {py_ver_str} (>= 3.10 supported)",
            }
        )
    else:
        has_critical_failure = True
        checks.append(
            {
                "name": "Python Version",
                "status": "fail",
                "critical": True,
                "details": f"Python {py_ver_str} is unsupported (>= 3.10 required)",
            }
        )

    # 2. Ray installation & version check
    try:
        import ray

        checks.append(
            {
                "name": "Ray Installation",
                "status": "pass",
                "critical": True,
                "details": f"Ray v{ray.__version__} installed and importable",
            }
        )
    except Exception as e:
        has_critical_failure = True
        checks.append(
            {
                "name": "Ray Installation",
                "status": "fail",
                "critical": True,
                "details": f"Failed to import Ray: {e}",
            }
        )

    # 3. Ray daemon / cluster session status
    try:
        daemon = RayDaemon()
        info = daemon.get_cluster_info()
        if info.get("is_running"):
            node_count = info.get("node_count", 1)
            addr = info.get("address") or "Local"
            checks.append(
                {
                    "name": "Ray Daemon / Cluster",
                    "status": "pass",
                    "critical": False,
                    "details": f"Cluster session active (Nodes: {node_count}, GCS: {addr})",
                }
            )
        else:
            checks.append(
                {
                    "name": "Ray Daemon / Cluster",
                    "status": "warn",
                    "critical": False,
                    "details": "Ray daemon session inactive (auto-starts on exercise run)",
                }
            )
    except Exception as e:
        checks.append(
            {
                "name": "Ray Daemon / Cluster",
                "status": "warn",
                "critical": False,
                "details": f"Could not query daemon: {e}",
            }
        )

    # 4. Exercises directory & manifest check
    exercises_dir = Path("exercises")
    try:
        manifest = get_manifest()
        total_ex = len(manifest.all_exercises)
        total_ch = len(manifest.chapters)
        if exercises_dir.exists() and total_ex > 0:
            checks.append(
                {
                    "name": "Exercises Manifest",
                    "status": "pass",
                    "critical": False,
                    "details": f"Found {total_ex} exercises across {total_ch} chapters in exercises/",
                }
            )
        elif total_ex > 0:
            checks.append(
                {
                    "name": "Exercises Manifest",
                    "status": "warn",
                    "critical": False,
                    "details": f"Curriculum manifest loaded ({total_ex} exercises), run 'raylings init' if exercises/ is missing",
                }
            )
        else:
            checks.append(
                {
                    "name": "Exercises Manifest",
                    "status": "warn",
                    "critical": False,
                    "details": "No exercises found. Run 'raylings init' to initialize workspace.",
                }
            )
    except Exception as e:
        checks.append(
            {
                "name": "Exercises Manifest",
                "status": "warn",
                "critical": False,
                "details": f"Could not inspect manifest: {e}",
            }
        )

    # 5. System CPU & Platform info
    cpu_count = os.cpu_count() or 1
    plat_str = f"{platform.system()} {platform.machine()}"
    ram_str = _get_ram_info()
    ram_part = f", {ram_str} RAM" if ram_str else ""
    sys_details = f"{cpu_count} logical CPUs ({plat_str}{ram_part})"
    if cpu_count >= 2:
        checks.append(
            {
                "name": "System Resources",
                "status": "pass",
                "critical": False,
                "details": sys_details,
            }
        )
    else:
        checks.append(
            {
                "name": "System Resources",
                "status": "warn",
                "critical": False,
                "details": f"{sys_details} - 2+ CPU cores recommended for Ray parallelism",
            }
        )

    return checks, has_critical_failure


@app.command(name="doctor")
def doctor_command(
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output doctor diagnostics as JSON",
    ),
) -> None:
    """Run preflight system and environment diagnostics."""
    checks, has_critical_failure = _run_doctor_diagnostics()

    passed_count = sum(1 for c in checks if c["status"] == "pass")
    warn_count = sum(1 for c in checks if c["status"] == "warn")
    fail_count = sum(1 for c in checks if c["status"] == "fail")

    overall_status = (
        "healthy"
        if fail_count == 0 and warn_count == 0
        else ("degraded" if fail_count == 0 else "error")
    )

    if as_json:
        import json

        print(
            json.dumps(
                {
                    "status": overall_status,
                    "passed": not has_critical_failure,
                    "summary": {
                        "total": len(checks),
                        "passed": passed_count,
                        "warnings": warn_count,
                        "failed": fail_count,
                    },
                    "checks": checks,
                },
                indent=2,
            )
        )
        if has_critical_failure:
            raise typer.Exit(1)
        return

    render_banner()
    table = Table(
        title="Preflight Diagnostics Summary",
        border_style="dim",
        header_style="bold magenta",
    )
    table.add_column("Diagnostic Check", style="bold cyan", width=26)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Details", style="white")

    from rich.markup import escape

    for check in checks:
        st = check["status"]
        status_markup = (
            "[bold green]✓ PASS[/bold green]"
            if st == "pass"
            else (
                "[bold yellow]! WARN[/bold yellow]"
                if st == "warn"
                else "[bold red]✗ FAIL[/bold red]"
            )
        )
        table.add_row(check["name"], status_markup, escape(check["details"]))

    console.print(table)
    console.print(
        f"\n[bold]Summary:[/bold] [bold green]{passed_count} passed[/bold green], "
        f"[bold yellow]{warn_count} warnings[/bold yellow], "
        f"[bold red]{fail_count} failed[/bold red]\n"
    )

    if has_critical_failure:
        raise typer.Exit(1)


@app.command(name="new", help="Scaffold a new exercise and solution template.")
@app.command(name="new-exercise", help="Scaffold a new exercise and solution template (alias).")
def new_command(
    chapter: str = typer.Argument(
        ...,
        help="Chapter number (e.g. 15 or 01) or chapter directory name (e.g. 15_vllm_and_llms)",
    ),
    name: str = typer.Argument(
        ...,
        help="Exercise filename/identifier without .py extension (e.g. vllm05)",
    ),
    title: str | None = typer.Option(
        None,
        "--title",
        "-t",
        help="Human-readable exercise title",
    ),
    description: str | None = typer.Option(
        None,
        "--description",
        "-d",
        help="Exercise description summary",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview scaffolded files and manifest entry without writing to disk",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output scaffolding result as JSON",
    ),
) -> None:
    """Scaffold a new exercise and reference solution template with boilerplate and manifest entry."""
    import json

    from rich.panel import Panel
    from rich.syntax import Syntax

    from raylings.scaffolder import ExerciseScaffolder

    scaffolder = ExerciseScaffolder()
    try:
        result = scaffolder.scaffold(
            chapter=chapter,
            name=name,
            title=title,
            description=description,
            dry_run=dry_run,
        )
    except Exception as e:
        if as_json:
            print(json.dumps({"error": str(e), "success": False}, indent=2))
        else:
            console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    if as_json:
        print(json.dumps(result.to_dict(dry_run=dry_run), indent=2))
        return

    render_banner()
    if dry_run:
        console.print(
            "[bold yellow]DRY RUN PREVIEW[/bold yellow] (No files were written to disk)\n"
        )
    else:
        console.print(
            f"[bold green]✓ Successfully scaffolded exercise '{result.exercise_name}'![/bold green]\n"
        )

    console.print(f"[bold cyan]Chapter:[/bold cyan] {result.chapter_name}")
    console.print(f"[bold cyan]Exercise File:[/bold cyan] {result.exercise_path}")
    console.print(f"[bold cyan]Solution File:[/bold cyan] {result.solution_path}\n")

    console.print(
        f"[bold magenta]Next Step:[/bold magenta] Register this exercise in [bold yellow]src/raylings/manifest.py[/bold yellow] under chapter [bold cyan]{result.chapter_name}[/bold cyan]:\n"
    )
    syntax = Syntax(result.manifest_snippet, "python", theme="monokai", line_numbers=False)
    console.print(Panel(syntax, title="Manifest Registration Snippet", border_style="cyan"))


@app.command(name="top", help="Display real-time cluster health and telemetry dashboard.")
def top_command(
    interval: float = typer.Option(
        1.0,
        "--interval",
        "-i",
        help="Refresh interval in seconds for live telemetry monitoring",
    ),
    once: bool = typer.Option(
        False,
        "--once",
        help="Capture and render a single cluster telemetry snapshot and exit",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output cluster telemetry snapshot as JSON",
    ),
) -> None:
    """Display real-time cluster health, node resources, Plasma object store metrics, and actor state."""
    from raylings.metrics import run_top_dashboard

    run_top_dashboard(interval=interval, once=once, as_json=as_json)


@app.command(name="metrics", help="Display cluster telemetry and resource metrics (alias for top).")
def metrics_command(
    interval: float = typer.Option(
        1.0,
        "--interval",
        "-i",
        help="Refresh interval in seconds for live telemetry monitoring",
    ),
    once: bool = typer.Option(
        False,
        "--once",
        help="Capture and render a single cluster telemetry snapshot and exit",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output cluster telemetry snapshot as JSON",
    ),
) -> None:
    """Display cluster telemetry, node resources, Plasma object store metrics, and actor state."""
    from raylings.metrics import run_top_dashboard

    run_top_dashboard(interval=interval, once=once, as_json=as_json)


@app.command(name="tui", help="Launch interactive full-screen split-pane TUI.")
def tui_command(
    exercise: str | None = typer.Option(
        None,
        "--exercise",
        "-e",
        help="Pre-select an exercise by name identifier (e.g. basics01)",
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        help="Render TUI once and exit (for headless tests / automation)",
    ),
) -> None:
    """Launch full-screen interactive split-pane TUI to browse exercises, inspect telemetry, and execute tasks."""
    from raylings.tui import run_tui_app

    try:
        run_tui_app(
            exercise_name=exercise,
            non_interactive=non_interactive,
        )
    except SystemExit as exc:
        if exc.code != 0:
            raise typer.Exit(exc.code)
    except Exception as e:
        console.print(f"[bold red]Error running TUI:[/bold red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
