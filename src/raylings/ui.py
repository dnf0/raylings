"""Rich terminal UI and diagnostics renderer for Raylings."""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from raylings.models import Exercise, Manifest
from raylings.runner import NOT_DONE_MARKER, RunResult

console = Console()

BANNER_ART = r"""
  ____             _ _
 |  _ \ __ _ _   _| (_)_ __   __ _ ___
 | |_) / _` | | | | | | '_ \ / _` / __|
 |  _ < (_| | |_| | | | | | | (_| \__ \
 |_| \_\__,_|\__, |_|_|_| |_|\__, |___/
             |___/           |___/
"""


def _get_console(c: Console | None) -> Console:
    return c if c is not None else console


def render_banner(console: Console | None = None) -> None:
    """Render the Raylings header banner with stylized branding and welcome message."""
    c = _get_console(console)
    banner_text = Text(BANNER_ART.strip(), style="bold cyan")
    tagline = Text(
        "\n⚡ RAYLINGS: Master Distributed Python with Ray from the Ground Up ⚡",
        style="bold yellow",
    )
    c.print(
        Panel(
            Text.assemble(banner_text, "\n", tagline, justify="center"),
            border_style="bright_blue",
            padding=(1, 2),
        )
    )
    c.print()


def render_result(result: RunResult, console: Console | None = None) -> None:
    """Display comprehensive diagnostics and feedback for an exercise execution result.

    Args:
        result: The RunResult instance returned by ExerciseRunner.
        console: Optional Rich console for rendering output.
    """
    c = _get_console(console)
    ex = result.exercise

    if result.passed:
        success_text = Text()
        success_text.append(f"✓ Exercise {ex.name} passed!\n\n", style="bold green")
        if result.output.strip():
            success_text.append(f"Output:\n{result.output.strip()}\n\n", style="dim white")
        success_text.append("Great job! Solution verified and complete.", style="bold cyan")
        c.print(
            Panel(
                success_text,
                title=f"[bold green]✓ SUCCESS: {ex.name} ({ex.title})[/bold green]",
                border_style="green",
            )
        )
    else:
        if result.has_not_done_marker:
            marker_notice = Text()
            marker_notice.append(
                f"Exercise {ex.name} still contains the '{NOT_DONE_MARKER}' marker.\n",
                style="bold yellow",
            )
            marker_notice.append(
                "When you are ready to evaluate your solution, remove this line at the top of the file.\n",
                style="yellow",
            )
            marker_notice.append(
                f"\nTip: Run `raylings hint {ex.name}` to get progressive hints.",
                style="dim cyan",
            )
            c.print(
                Panel(
                    marker_notice,
                    title=f"[bold yellow]⌛ PENDING: {ex.name} ({ex.title})[/bold yellow]",
                    border_style="yellow",
                )
            )

        if result.error:
            if result.output:
                c.print(
                    Panel(
                        result.output.strip(),
                        title=f"[bold cyan]Standard Output: {ex.name}[/bold cyan]",
                        border_style="cyan",
                    )
                )
            c.print(
                Panel(
                    result.error.strip(),
                    title=f"[bold red]✗ FAILURE: {ex.name} - Error Traceback[/bold red]",
                    border_style="red",
                )
            )
        elif result.output and not result.passed:
            c.print(
                Panel(
                    result.output.strip(),
                    title=f"[bold yellow]Output: {ex.name}[/bold yellow]",
                    border_style="yellow",
                )
            )


def render_success_prompt(
    exercise: Exercise,
    next_exercise: Exercise | None = None,
    console: Console | None = None,
) -> None:
    """Render interactive success banner with keystroke navigation controls."""
    c = _get_console(console)
    next_info = f" ({next_exercise.name})" if next_exercise else " (All Finished!)"
    nav_text = Text()
    nav_text.append(f"✓ {exercise.name} passed!\n\n", style="bold green")
    nav_text.append("Interactive Controls:\n", style="bold white")
    nav_text.append(f"  [n / Enter]  Advance to next exercise{next_info}\n", style="bold cyan")
    nav_text.append("  [p]          Go to previous exercise\n", style="bold cyan")
    nav_text.append("  [r]          Rerun current exercise\n", style="bold cyan")
    nav_text.append("  [h]          Show progressive hint\n", style="bold cyan")
    nav_text.append("  [q]          Quit watcher\n", style="bold cyan")
    c.print(
        Panel(
            nav_text,
            title=f"[bold green]🎉 SUCCESS: {exercise.name} ({exercise.title})[/bold green]",
            border_style="green",
        )
    )


def render_failure_prompt(
    exercise: Exercise,
    console: Console | None = None,
) -> None:
    """Render interactive failure prompt with hint and rerun navigation options."""
    c = _get_console(console)
    nav_text = Text()
    nav_text.append(f"Exercise {exercise.name} is not passing yet.\n\n", style="yellow")
    nav_text.append("Interactive Controls:\n", style="bold white")
    nav_text.append("  [h]          Reveal progressive hint\n", style="bold cyan")
    nav_text.append("  [r]          Rerun exercise after editing\n", style="bold cyan")
    nav_text.append("  [n]          Skip to next exercise\n", style="bold cyan")
    nav_text.append("  [p]          Go back to previous exercise\n", style="bold cyan")
    nav_text.append("  [q]          Quit watcher\n", style="bold cyan")
    c.print(
        Panel(
            nav_text,
            title=f"[bold yellow]⏳ PENDING: {exercise.name} ({exercise.title})[/bold yellow]",
            border_style="yellow",
        )
    )


def render_hint(exercise: Exercise, hint_level: int = 0, console: Console | None = None) -> None:
    """Display progressive hints for an exercise.

    Args:
        exercise: Target Exercise instance.
        hint_level: Zero-indexed hint level to display.
        console: Optional Rich console for rendering output.
    """
    c = _get_console(console)

    if not exercise.hints:
        c.print(
            Panel(
                f"No hints available for exercise [bold]{exercise.name}[/bold].",
                title=f"[yellow]💡 Hints: {exercise.name}[/yellow]",
                border_style="yellow",
            )
        )
        return

    total_hints = len(exercise.hints)
    idx = min(max(0, hint_level), total_hints - 1)
    hint_content = exercise.hints[idx]

    hint_text = Text()
    hint_text.append(f"{hint_content}\n\n", style="white")
    if idx + 1 < total_hints:
        hint_text.append(
            f"Next hint: run `raylings hint {exercise.name} --level {idx + 2}`",
            style="dim cyan",
        )
    else:
        hint_text.append("(All hints for this exercise revealed!)", style="dim green")

    c.print(
        Panel(
            hint_text,
            title=f"[bold yellow]💡 Hint ({idx + 1}/{total_hints}) for {exercise.name}: {exercise.title}[/bold yellow]",
            border_style="yellow",
        )
    )


def render_progress(
    manifest: Manifest,
    completed_count: int = 0,
    console: Console | None = None,
) -> None:
    """Render overall curriculum progress bar and chapter breakdown table.

    Args:
        manifest: The curriculum Manifest instance.
        completed_count: Total number of completed exercises.
        console: Optional Rich console for rendering output.
    """
    c = _get_console(console)
    all_exercises = manifest.all_exercises
    total_exercises = len(all_exercises)
    pct = (completed_count / total_exercises * 100) if total_exercises > 0 else 0.0

    bar_len = 30
    filled_len = int(bar_len * completed_count // total_exercises) if total_exercises > 0 else 0
    bar = (
        "━" * filled_len + "╸" + " " * max(0, bar_len - filled_len - 1)
        if filled_len < bar_len
        else "━" * bar_len
    )

    progress_header = Text()
    progress_header.append("Overall Curriculum Progress: ", style="bold white")
    progress_header.append(f"[{bar}] ", style="bold cyan")
    progress_header.append(
        f"{completed_count}/{total_exercises} ({pct:.1f}%)\n", style="bold green"
    )
    c.print(progress_header)

    table = Table(
        title="Curriculum Chapters & Exercises",
        border_style="dim",
        header_style="bold magenta",
    )
    table.add_column("Ch #", justify="center", style="cyan", width=6)
    table.add_column("Chapter Title", style="bold white", width=36)
    table.add_column("Exercises", justify="center", style="yellow", width=12)
    table.add_column("Description", style="dim white")

    for ch in manifest.chapters:
        table.add_row(
            str(ch.number),
            ch.title,
            f"{len(ch.exercises)} exercises",
            ch.description,
        )

    c.print(table)


def render_cluster_status(
    cluster_info: dict[str, Any],
    console: Console | None = None,
) -> None:
    """Render Ray daemon / cluster status panel with hardware and resource statistics.

    Args:
        cluster_info: Dictionary containing cluster runtime metadata.
        console: Optional Rich console for rendering output.
    """
    c = _get_console(console)
    is_running = cluster_info.get("is_running", False)

    if not is_running:
        c.print(
            Panel(
                "[yellow]Ray daemon session is currently inactive or stopped.[/yellow]\n"
                "Session will automatically start when running exercises.",
                title="[bold yellow]⚡ Ray Cluster Status: Inactive[/bold yellow]",
                border_style="yellow",
            )
        )
        return

    address = cluster_info.get("address", "Local")
    node_count = cluster_info.get("node_count", 1)
    cluster_resources = cluster_info.get("cluster_resources", {})
    available_resources = cluster_info.get("available_resources", {})

    cpus = cluster_resources.get("CPU", 0.0)
    avail_cpus = available_resources.get("CPU", cpus)
    object_mem = cluster_resources.get("object_store_memory", 0.0)
    object_mem_mb = object_mem / (1024 * 1024)

    status_text = Text()
    status_text.append("• Status:       Active & Running\n", style="bold green")
    status_text.append(f"• GCS Address:  {address}\n", style="white")
    status_text.append(f"• Nodes:        {node_count} active node(s)\n", style="white")
    status_text.append(f"• CPUs:         {avail_cpus:.1f} / {cpus:.1f} available\n", style="white")
    status_text.append(f"• Object Store: {object_mem_mb:.1f} MB allocated\n", style="white")

    c.print(
        Panel(
            status_text,
            title="[bold green]⚡ Ray Cluster Status: Active[/bold green]",
            border_style="green",
        )
    )
