"""Interactive Full-Screen Split-Pane TUI for Raylings learning framework."""

import os
import platform
import select
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.live import Live
from rich.markup import escape
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from raylings import __version__
from raylings.manifest import get_manifest
from raylings.metrics import (
    ClusterMetricsCollector,
    ClusterSnapshot,
    render_metrics_dashboard,
)
from raylings.models import Chapter, Exercise, Manifest
from raylings.runner import ExerciseRunner, RunResult
from raylings.state import StateTracker, get_state_tracker


class TUIViewMode(str, Enum):
    """View modes supported by the interactive TUI."""

    EXERCISE = "exercise"
    TELEMETRY = "telemetry"
    DOCTOR = "doctor"


class TUIAction(str, Enum):
    """Action codes dispatched from keyboard events in the TUI."""

    NEXT = "next"
    PREV = "prev"
    RUN = "run"
    HINT = "hint"
    TELEMETRY = "telemetry"
    DOCTOR = "doctor"
    QUIT = "quit"
    NONE = "none"


@dataclass
class TUIState:
    """Manages the UI state, navigation index, hint cycling, and run diagnostics."""

    manifest: Manifest
    tracker: StateTracker
    current_exercise_idx: int = 0
    view_mode: TUIViewMode = TUIViewMode.EXERCISE
    hint_level: int = 0
    show_hint: bool = False
    last_run_result: RunResult | None = None
    status_message: str = ""
    results_by_name: dict[str, RunResult] = field(default_factory=dict)

    @property
    def all_exercises(self) -> list[Exercise]:
        """Return flattened list of all curriculum exercises."""
        return self.manifest.all_exercises

    @property
    def current_exercise(self) -> Exercise | None:
        """Return the currently selected Exercise or None if manifest is empty."""
        exercises = self.all_exercises
        if not exercises:
            return None
        idx = max(0, min(self.current_exercise_idx, len(exercises) - 1))
        return exercises[idx]

    @property
    def current_chapter(self) -> Chapter | None:
        """Return the Chapter that contains the currently selected exercise."""
        curr = self.current_exercise
        if curr is None:
            return None
        for ch in self.manifest.chapters:
            if curr in ch.exercises:
                return ch
        return None

    def next_exercise(self) -> Exercise | None:
        """Advance to the next exercise in curriculum order."""
        exercises = self.all_exercises
        if not exercises:
            return None
        if self.current_exercise_idx < len(exercises) - 1:
            self.current_exercise_idx += 1
            self.show_hint = False
            if self.current_exercise:
                self.last_run_result = self.results_by_name.get(self.current_exercise.name)
        return self.current_exercise

    def prev_exercise(self) -> Exercise | None:
        """Move to the previous exercise in curriculum order."""
        exercises = self.all_exercises
        if not exercises:
            return None
        if self.current_exercise_idx > 0:
            self.current_exercise_idx -= 1
            self.show_hint = False
            self.hint_level = 0
            if self.current_exercise:
                self.last_run_result = self.results_by_name.get(self.current_exercise.name)
        return self.current_exercise

    def select_exercise_by_name(self, name: str) -> bool:
        """Select an exercise by name identifier.

        Args:
            name: Exercise name (e.g. 'basics01').

        Returns:
            True if found and selected, False otherwise.
        """
        for idx, ex in enumerate(self.all_exercises):
            if ex.name == name:
                self.current_exercise_idx = idx
                self.show_hint = False
                self.hint_level = 0
                self.last_run_result = self.results_by_name.get(ex.name)
                return True
        return False

    def toggle_hint(self) -> int:
        """Toggle or cycle the active hint level for the current exercise.

        Returns:
            Current hint level index (0-indexed).
        """
        curr = self.current_exercise
        if curr is None or not curr.hints:
            self.show_hint = True
            self.hint_level = 0
            return 0

        if not self.show_hint:
            self.show_hint = True
            self.hint_level = 0
        else:
            self.hint_level = (self.hint_level + 1) % len(curr.hints)
        return self.hint_level

    def toggle_telemetry(self) -> TUIViewMode:
        """Toggle telemetry overlay view mode."""
        if self.view_mode == TUIViewMode.TELEMETRY:
            self.view_mode = TUIViewMode.EXERCISE
        else:
            self.view_mode = TUIViewMode.TELEMETRY
        return self.view_mode

    def toggle_doctor(self) -> TUIViewMode:
        """Toggle doctor preflight diagnostics view mode."""
        if self.view_mode == TUIViewMode.DOCTOR:
            self.view_mode = TUIViewMode.EXERCISE
        else:
            self.view_mode = TUIViewMode.DOCTOR
        return self.view_mode

    def record_run_result(self, result: RunResult) -> None:
        """Record the execution outcome of an exercise and update persistence state."""
        self.last_run_result = result
        self.results_by_name[result.exercise.name] = result
        self.tracker.mark_completed(result.exercise.name, result.passed)
        self.show_hint = False


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


def run_doctor_checks() -> list[dict[str, Any]]:
    """Execute preflight system and environment diagnostics checks for TUI."""
    checks: list[dict[str, Any]] = []

    # 1. Python version check
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
        checks.append(
            {
                "name": "Python Version",
                "status": "fail",
                "critical": True,
                "details": f"Python {py_ver_str} is unsupported (>= 3.10 required)",
            }
        )

    # 2. Ray installation
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
        checks.append(
            {
                "name": "Ray Installation",
                "status": "fail",
                "critical": True,
                "details": f"Failed to import Ray: {e}",
            }
        )

    # 3. Ray daemon session status
    try:
        from raylings.daemon import RayDaemon

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

    # 4. Exercises manifest
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
        else:
            checks.append(
                {
                    "name": "Exercises Manifest",
                    "status": "warn",
                    "critical": False,
                    "details": f"Curriculum manifest loaded ({total_ex} exercises)",
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

    # 5. System Resources
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

    return checks


def create_tui_layout(
    state: TUIState,
    metrics_snapshot: ClusterSnapshot | None = None,
    doctor_checks: list[dict[str, Any]] | None = None,
) -> Layout:
    """Construct a full-screen split-pane Rich Layout from current TUIState.

    Layout Hierarchy:
      root:
        ├── header (height=3)
        ├── body (split horizontally into sidebar and main)
        │     ├── sidebar (width=36)
        │     └── main (split vertically into code_panel and output_panel)
        └── footer (height=3)

    Args:
        state: TUIState holding curriculum, navigation, and results.
        metrics_snapshot: Optional snapshot for telemetry mode.
        doctor_checks: Optional diagnostic checks list for doctor mode.

    Returns:
        Configured Rich Layout.
    """
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3),
    )

    # 1. Header Bar
    completed_count = len(
        state.tracker.get_completed_set().intersection({e.name for e in state.all_exercises})
    )
    total_count = len(state.all_exercises)
    pct = (completed_count / total_count * 100.0) if total_count > 0 else 0.0

    header_table = Table.grid(expand=True, padding=(0, 2))
    header_table.add_column("Title", style="bold cyan", justify="left")
    header_table.add_column("Progress", style="bold green", justify="right")

    header_table.add_row(
        f"⚡ [bold cyan]Raylings[/bold cyan] [dim]v{__version__}[/dim] — Interactive Ray Learning TUI",
        f"Progress: [bold green]{completed_count}/{total_count}[/bold green] ([bold cyan]{pct:.1f}%[/bold cyan])",
    )
    layout["header"].update(
        Panel(header_table, style="bold bright_blue", border_style="blue", padding=(0, 1))
    )

    # 2. Sidebar Tree
    tree = Tree("[bold cyan]Curriculum Chapters[/bold cyan]")
    curr_ex = state.current_exercise

    for ch in state.manifest.chapters:
        ch_completed = sum(
            1
            for e in ch.exercises
            if state.tracker.is_completed(e.name)
            or (e.name in state.results_by_name and state.results_by_name[e.name].passed)
        )
        ch_node = tree.add(
            f"[bold magenta]Ch {ch.number:02d}: {ch.title}[/bold magenta] [dim]({ch_completed}/{len(ch.exercises)})[/dim]"
        )

        for ex in ch.exercises:
            is_done = state.tracker.is_completed(ex.name) or (
                ex.name in state.results_by_name and state.results_by_name[ex.name].passed
            )
            is_failed = (
                ex.name in state.results_by_name and not state.results_by_name[ex.name].passed
            )
            is_active = (curr_ex is not None) and (ex.name == curr_ex.name)

            if is_done:
                icon = "[bold green]✓[/bold green]"
            elif is_failed or is_active:
                icon = "[bold yellow]⏳[/bold yellow]"
            else:
                icon = "[dim]○[/dim]"

            if is_active:
                label = f"[bold white on blue] > {icon} {ex.name} [/bold white on blue]"
            else:
                label = f"  {icon} [white]{ex.name}[/white]"
            ch_node.add(label)

    sidebar_panel = Panel(
        tree,
        title="[bold cyan]Exercises[/bold cyan]",
        border_style="cyan",
        padding=(0, 1),
    )

    # 3. Main Body Split
    layout["body"].split_row(
        Layout(name="sidebar", size=36),
        Layout(name="main", ratio=1),
    )
    layout["body"]["sidebar"].update(sidebar_panel)

    # Render Main view based on active mode
    if state.view_mode == TUIViewMode.TELEMETRY:
        snap = metrics_snapshot
        if snap is None:
            collector = ClusterMetricsCollector()
            snap = collector.collect_snapshot()
        telemetry_renderable = render_metrics_dashboard(snap)
        layout["body"]["main"].update(
            Panel(
                telemetry_renderable,
                title="[bold green]⚡ Ray Cluster Telemetry Inspector (Press 't' or 'Esc' to exit)[/bold green]",
                border_style="green",
            )
        )
    elif state.view_mode == TUIViewMode.DOCTOR:
        checks = doctor_checks if doctor_checks is not None else run_doctor_checks()
        doc_table = Table(
            title="Preflight Diagnostics Summary",
            border_style="dim",
            header_style="bold magenta",
            expand=True,
        )
        doc_table.add_column("Diagnostic Check", style="bold cyan", width=24)
        doc_table.add_column("Status", justify="center", width=12)
        doc_table.add_column("Details", style="white")

        for c in checks:
            st = c["status"]
            status_markup = (
                "[bold green]✓ PASS[/bold green]"
                if st == "pass"
                else (
                    "[bold yellow]! WARN[/bold yellow]"
                    if st == "warn"
                    else "[bold red]✗ FAIL[/bold red]"
                )
            )
            doc_table.add_row(c["name"], status_markup, escape(c["details"]))

        layout["body"]["main"].update(
            Panel(
                doc_table,
                title="[bold yellow]🩺 System & Environment Preflight Diagnostics (Press 'd' or 'Esc' to exit)[/bold yellow]",
                border_style="yellow",
            )
        )
    else:
        # EXERCISE MODE: Split main vertically into Code panel (top) and Output panel (bottom)
        layout["body"]["main"].split_column(
            Layout(name="code_panel", ratio=1),
            Layout(name="output_panel", ratio=1),
        )

        # Code preview panel
        if curr_ex is not None:
            content = ""
            if curr_ex.file_path.exists():
                try:
                    content = curr_ex.file_path.read_text(encoding="utf-8")
                except Exception as e:
                    content = f"# Error reading exercise file: {e}"
            else:
                content = f"# Exercise file '{curr_ex.path}' not found.\n# Run 'raylings init' to initialize exercises."

            code_syntax = Syntax(
                content,
                "python",
                theme="monokai",
                line_numbers=True,
                word_wrap=True,
            )
            code_title = f"[bold yellow]Exercise: {curr_ex.name} — {curr_ex.title}[/bold yellow]"
            layout["body"]["main"]["code_panel"].update(
                Panel(code_syntax, title=code_title, border_style="yellow", padding=(0, 1))
            )
        else:
            layout["body"]["main"]["code_panel"].update(
                Panel("[dim]No exercises available.[/dim]", border_style="yellow")
            )

        # Output / Hint panel
        output_content: RenderableType
        output_title = "[bold green]Output & Diagnostics[/bold green]"

        if state.show_hint and curr_ex is not None:
            if curr_ex.hints:
                hint_idx = min(state.hint_level, len(curr_ex.hints) - 1)
                hint_text = curr_ex.hints[hint_idx]
                output_title = f"[bold yellow]💡 Progressive Hint ({hint_idx + 1}/{len(curr_ex.hints)})[/bold yellow]"
                hint_renderable = Text()
                hint_renderable.append(
                    f"Hint {hint_idx + 1} of {len(curr_ex.hints)}:\n\n",
                    style="bold yellow",
                )
                hint_renderable.append(f"{hint_text}\n\n", style="bold white")
                hint_renderable.append(
                    "[dim]Press 'h' again to cycle to next hint.[/dim]", style="dim"
                )
                output_content = hint_renderable
            else:
                output_title = "[bold yellow]💡 Progressive Hints[/bold yellow]"
                output_content = Text(
                    "No hints available for this exercise.", style="italic yellow"
                )
        elif state.last_run_result is not None:
            res = state.last_run_result
            res_text = Text()
            if res.passed:
                res_text.append("✓ PASSED\n\n", style="bold green")
                if res.output:
                    res_text.append(res.output, style="white")
            else:
                res_text.append(f"✗ FAILED (exit code {res.exit_code})\n\n", style="bold red")
                if res.has_not_done_marker:
                    res_text.append(
                        "File contains incomplete placeholders or pending tasks.\n\n",
                        style="yellow",
                    )
                if res.error:
                    res_text.append(res.error, style="red")
                elif res.output:
                    res_text.append(res.output, style="white")
            output_content = res_text
        else:
            prompt_text = Text()
            prompt_text.append("Ready to run exercise!\n\n", style="bold cyan")
            prompt_text.append(" • Press ", style="white")
            prompt_text.append("r", style="bold yellow")
            prompt_text.append(" to run this exercise\n", style="white")
            prompt_text.append(" • Press ", style="white")
            prompt_text.append("h", style="bold yellow")
            prompt_text.append(" to reveal progressive hints\n", style="white")
            prompt_text.append(" • Press ", style="white")
            prompt_text.append("t", style="bold yellow")
            prompt_text.append(" to inspect cluster telemetry\n", style="white")
            prompt_text.append(" • Press ", style="white")
            prompt_text.append("d", style="bold yellow")
            prompt_text.append(" for system doctor diagnostics\n", style="white")
            prompt_text.append(" • Press ", style="white")
            prompt_text.append("j / k", style="bold yellow")
            prompt_text.append(" (or ↑ / ↓) to navigate exercises", style="white")
            output_content = prompt_text

        layout["body"]["main"]["output_panel"].update(
            Panel(output_content, title=output_title, border_style="green", padding=(0, 1))
        )

    # 4. Keybinding Footer
    footer_text = Text()
    footer_text.append(" [bold cyan]j/↓/n[/bold cyan] Next | ")
    footer_text.append("[bold cyan]k/↑/p[/bold cyan] Prev | ")
    footer_text.append("[bold cyan]r[/bold cyan] Run | ")
    footer_text.append("[bold cyan]h[/bold cyan] Hint | ")
    footer_text.append("[bold cyan]t[/bold cyan] Telemetry | ")
    footer_text.append("[bold cyan]d[/bold cyan] Doctor | ")
    footer_text.append("[bold cyan]q[/bold cyan] Quit")

    if state.status_message:
        footer_text.append(f"  [bold yellow]⚡ {state.status_message}[/bold yellow]")

    layout["footer"].update(Panel(footer_text, border_style="dim", padding=(0, 1)))

    return layout


def handle_key(key: str, state: TUIState) -> TUIAction:
    """Process a key event and update TUIState accordingly.

    Args:
        key: Key string (e.g. 'j', 'down', 'k', 'up', 'r', 'h', 't', 'd', 'q', 'escape').
        state: TUIState to update.

    Returns:
        Dispatched TUIAction enum member.
    """
    k = key.lower().strip()

    if k in ("j", "down", "n", "\x1b[b"):
        state.next_exercise()
        return TUIAction.NEXT
    if k in ("k", "up", "p", "\x1b[a"):
        state.prev_exercise()
        return TUIAction.PREV
    if k == "r":
        return TUIAction.RUN
    if k == "h":
        state.toggle_hint()
        return TUIAction.HINT
    if k == "t":
        state.toggle_telemetry()
        return TUIAction.TELEMETRY
    if k == "d":
        state.toggle_doctor()
        return TUIAction.DOCTOR
    if k in ("q", "quit"):
        return TUIAction.QUIT
    if k in ("escape", "e") and state.view_mode != TUIViewMode.EXERCISE:
        state.view_mode = TUIViewMode.EXERCISE
        return TUIAction.NONE

    return TUIAction.NONE


def _read_single_key(timeout: float = 0.1) -> str | None:
    """Read a single character or escape sequence from stdin non-blockingly."""
    if not sys.stdin.isatty():
        return None
    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if rlist:
                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    rlist2, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if rlist2:
                        ch2 = sys.stdin.read(1)
                        if ch2 == "[":
                            ch3 = sys.stdin.read(1)
                            if ch3 == "A":
                                return "up"
                            elif ch3 == "B":
                                return "down"
                            elif ch3 == "C":
                                return "right"
                            elif ch3 == "D":
                                return "left"
                            return f"\x1b[{ch3}"
                        return f"\x1b{ch2}"
                    return "escape"
                return ch
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        return None


class RaylingsTUI:
    """Full-screen split-pane terminal user interface for the Raylings curriculum."""

    def __init__(
        self,
        manifest: Manifest | None = None,
        runner: ExerciseRunner | None = None,
        tracker: StateTracker | None = None,
        collector: ClusterMetricsCollector | None = None,
        console: Console | None = None,
    ) -> None:
        """Initialize the Raylings TUI controller.

        Args:
            manifest: Optional Manifest instance.
            runner: Optional ExerciseRunner instance.
            tracker: Optional StateTracker instance.
            collector: Optional ClusterMetricsCollector instance.
            console: Optional Rich Console instance.
        """
        self.manifest = manifest if manifest is not None else get_manifest()
        self.tracker = tracker if tracker is not None else get_state_tracker()
        self.runner = runner if runner is not None else ExerciseRunner()
        self.collector = collector if collector is not None else ClusterMetricsCollector()
        self.console = console if console is not None else Console()
        self.state = TUIState(manifest=self.manifest, tracker=self.tracker)

    def run_current_exercise(self) -> RunResult:
        """Execute the currently selected exercise and record its outcome."""
        ex = self.state.current_exercise
        if ex is None:
            res = RunResult(
                exercise=Exercise(name="none", title="none", path="", chapter_name=""),
                passed=False,
                has_not_done_marker=False,
                output="",
                error="No exercise currently selected.",
                exit_code=1,
            )
            return res

        res = self.runner.run_exercise(ex)
        self.state.record_run_result(res)
        return res

    def render(self) -> Layout:
        """Construct the Rich Layout representation of current TUI state."""
        metrics_snap = None
        if self.state.view_mode == TUIViewMode.TELEMETRY:
            metrics_snap = self.collector.collect_snapshot()

        doctor_checks = None
        if self.state.view_mode == TUIViewMode.DOCTOR:
            doctor_checks = run_doctor_checks()

        return create_tui_layout(
            self.state,
            metrics_snapshot=metrics_snap,
            doctor_checks=doctor_checks,
        )

    def render_once(self, exercise_name: str | None = None) -> None:
        """Render the TUI once in headless non-interactive mode.

        Args:
            exercise_name: Optional exercise name to select before rendering.
        """
        if exercise_name:
            self.state.select_exercise_by_name(exercise_name)
        layout = self.render()
        self.console.print(layout)

    def run_interactive(self, initial_exercise: str | None = None) -> None:
        """Start full-screen live interactive TUI loop.

        Args:
            initial_exercise: Optional initial exercise name to select.
        """
        if initial_exercise:
            self.state.select_exercise_by_name(initial_exercise)

        try:
            with Live(
                self.render(),
                console=self.console,
                screen=True,
                refresh_per_second=10,
            ) as live:
                while True:
                    key = _read_single_key(timeout=0.1)
                    if key is None:
                        continue

                    action = handle_key(key, self.state)
                    if action == TUIAction.QUIT:
                        break

                    if action == TUIAction.RUN:
                        self.state.status_message = "Running..."
                        live.update(self.render())
                        self.run_current_exercise()
                        self.state.status_message = ""
                        live.update(self.render())
                    else:
                        live.update(self.render())
        except KeyboardInterrupt:
            pass


def run_tui_app(
    exercise_name: str | None = None,
    non_interactive: bool = False,
    console: Console | None = None,
) -> None:
    """Entrypoint function to run Raylings TUI from CLI.

    Args:
        exercise_name: Optional initial exercise name.
        non_interactive: If True, renders snapshot once and returns.
        console: Optional Console instance.
    """
    c = console or Console()
    tui = RaylingsTUI(console=c)

    if exercise_name:
        found = tui.state.select_exercise_by_name(exercise_name)
        if not found:
            c.print(f"[bold red]Exercise '{exercise_name}' not found in curriculum.[/bold red]")
            raise SystemExit(1)

    if non_interactive or not sys.stdin.isatty():
        tui.render_once(exercise_name=exercise_name)
        return

    tui.run_interactive(initial_exercise=exercise_name)
