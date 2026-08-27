"""File watcher loop and interactive exercise evaluator."""

import logging
import queue
import select
import sys
import threading
from pathlib import Path
from typing import Any

from raylings.daemon import RayDaemon
from raylings.manifest import get_manifest, get_next_exercise, get_previous_exercise
from raylings.models import Exercise, Manifest
from raylings.runner import ExerciseRunner, RunResult
from raylings.state import StateTracker, get_state_tracker
from raylings.ui import (
    console,
    render_banner,
    render_failure_prompt,
    render_hint,
    render_progress,
    render_result,
    render_success_prompt,
)

logger = logging.getLogger("raylings.watcher")


def _read_single_key(timeout: float = 0.2) -> str | None:
    """Read a single character from stdin if TTY is attached, otherwise return None."""
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
                return sys.stdin.read(1)
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        return None


class ExerciseWatcher:
    """Monitors exercise file modifications and coordinates interactive evaluation."""

    def __init__(
        self,
        manifest: Manifest | None = None,
        runner: ExerciseRunner | None = None,
        daemon: RayDaemon | None = None,
        tracker: StateTracker | None = None,
    ) -> None:
        """Initialize the ExerciseWatcher.

        Args:
            manifest: Optional curriculum Manifest instance (defaults to get_manifest()).
            runner: Optional ExerciseRunner instance.
            daemon: Optional RayDaemon session manager.
            tracker: Optional StateTracker instance.
        """
        self.manifest = manifest if manifest is not None else get_manifest()
        self.runner = runner if runner is not None else ExerciseRunner()
        self.daemon = daemon
        self.tracker = tracker if tracker is not None else get_state_tracker()
        self._current_exercise: Exercise | None = None
        self._hint_level: int = 0

    def find_current_exercise(self) -> Exercise | None:
        """Scan curriculum exercises in order and locate the first incomplete exercise.

        Uses local state tracking cache for instant resolution.

        Returns:
            Exercise instance if an incomplete exercise is found, or None if all are completed.
        """
        for ex in self.manifest.all_exercises:
            if not ex.file_path.exists():
                self._current_exercise = ex
                return ex

            if self.tracker.is_completed(ex.name):
                continue

            res = self.runner.run_exercise(ex, timeout=5.0)
            if res.passed:
                self.tracker.mark_completed(ex.name, True)
            else:
                self._current_exercise = ex
                return ex

        self._current_exercise = None
        return None

    def evaluate_exercise(self, exercise: Exercise) -> RunResult:
        """Execute an exercise and render diagnostics to the console.

        Args:
            exercise: The Exercise to evaluate.

        Returns:
            RunResult produced by ExerciseRunner.
        """
        res = self.runner.run_exercise(exercise)
        self.tracker.mark_completed(exercise.name, res.passed)
        render_result(res)

        next_ex = get_next_exercise(exercise.name)
        if res.passed:
            render_success_prompt(exercise, next_exercise=next_ex)
        else:
            render_failure_prompt(exercise)
        return res

    def on_file_changed(self, file_path: Path) -> RunResult | None:
        """Handle a file modification event by matching against known curriculum exercises.

        Args:
            file_path: The Path of the modified file.

        Returns:
            RunResult if the modified file matches an exercise, or None otherwise.
        """
        resolved_target = file_path.resolve() if file_path.exists() else file_path
        for ex in self.manifest.all_exercises:
            resolved_ex = ex.file_path.resolve() if ex.file_path.exists() else ex.file_path
            if (
                resolved_ex == resolved_target
                or file_path.name == ex.file_path.name
                or str(file_path).endswith(ex.path)
            ):
                self._current_exercise = ex
                self._hint_level = 0
                return self.evaluate_exercise(ex)
        return None

    def watch_loop(self, exercise_dir: Path = Path("exercises")) -> None:
        """Start the continuous file watcher loop over the exercises directory.

        Args:
            exercise_dir: Path to directory containing exercise files.
        """
        if self.daemon is not None:
            console.print("[cyan]Pre-warming Ray daemon session...[/cyan]")
            self.daemon.ensure_started()

        render_banner()

        if not exercise_dir.exists():
            console.print(
                f"[bold yellow]Directory '{exercise_dir}' not found in current working directory.[/bold yellow]\n\n"
                "To initialize the interactive Ray exercises in this folder, run:\n"
                "  [bold cyan]raylings init[/bold cyan]\n"
            )
            return

        curr = self.find_current_exercise()
        if curr is None:
            console.print(
                "[bold green]🎉 All Raylings exercises completed! Great work![/bold green]\n"
            )
            if self.manifest.all_exercises:
                curr = self.manifest.all_exercises[0]
        else:
            console.print(
                f"[bold cyan]Current exercise:[/bold cyan] [bold yellow]{curr.name}[/bold yellow] ({curr.title})\n"
            )
            self.evaluate_exercise(curr)

        console.print(f"\n[dim]👀 Watching for file changes in '{exercise_dir}'...[/dim]\n")

        # In non-interactive environments (CI, pytest), run simple file watch loop
        if not sys.stdin.isatty():
            try:
                import watchfiles

                for changes in watchfiles.watch(exercise_dir):
                    for _change_type, path_str in changes:
                        p = Path(path_str)
                        if p.suffix == ".py":
                            self.on_file_changed(p)
            except KeyboardInterrupt:
                console.print("\n[yellow]Exiting Raylings watch mode. Keep learning![/yellow]")
            finally:
                if self.daemon is not None:
                    self.daemon.stop()
            return

        # In interactive TTY environment, run keystroke + file change concurrent loop
        stop_event = threading.Event()
        change_queue: queue.Queue[Path] = queue.Queue()

        def _file_watch_worker():
            try:
                import watchfiles

                for changes in watchfiles.watch(exercise_dir, stop_event=stop_event):
                    for _change_type, path_str in changes:
                        p = Path(path_str)
                        if p.suffix == ".py":
                            change_queue.put(p)
            except Exception:
                pass

        watch_thread = threading.Thread(target=_file_watch_worker, daemon=True)
        watch_thread.start()

        try:
            while not stop_event.is_set():
                # Check for file changes
                try:
                    while True:
                        changed_file = change_queue.get_nowait()
                        res = self.on_file_changed(changed_file)
                        if res is not None:
                            curr = res.exercise
                except queue.Empty:
                    pass

                # Check for keyboard inputs
                key = _read_single_key(timeout=0.2)
                if key is None:
                    continue

                k = key.lower()
                if k in ("\n", "\r", "n"):
                    # Advance to next exercise
                    if curr is not None:
                        nxt = get_next_exercise(curr.name)
                        if nxt is not None:
                            curr = nxt
                            self._hint_level = 0
                            console.print(
                                f"\n[bold cyan]Switching to:[/bold cyan] [bold yellow]{curr.name}[/bold yellow] ({curr.title})"
                            )
                            self.evaluate_exercise(curr)
                        else:
                            console.print("\n[green]You are already at the final exercise![/green]")
                elif k == "p":
                    # Go to previous exercise
                    if curr is not None:
                        prev = get_previous_exercise(curr.name)
                        if prev is not None:
                            curr = prev
                            self._hint_level = 0
                            console.print(
                                f"\n[bold cyan]Switching to:[/bold cyan] [bold yellow]{curr.name}[/bold yellow] ({curr.title})"
                            )
                            self.evaluate_exercise(curr)
                        else:
                            console.print(
                                "\n[yellow]You are already at the first exercise![/yellow]"
                            )
                elif k == "r":
                    # Rerun current exercise
                    if curr is not None:
                        console.print(f"\n[cyan]Rerunning {curr.name}...[/cyan]")
                        self.evaluate_exercise(curr)
                elif k == "h":
                    # Show progressive hint
                    if curr is not None:
                        render_hint(curr, hint_level=self._hint_level)
                        if curr.hints:
                            self._hint_level = (self._hint_level + 1) % len(curr.hints)
                elif k == "l":
                    # Render overall progress
                    render_progress(self.manifest)
                elif k == "q":
                    console.print("\n[yellow]Exiting Raylings watch mode. Keep learning![/yellow]")
                    break

        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting Raylings watch mode. Keep learning![/yellow]")
        except Exception as exc:
            logger.error("Error encountered during watch loop: %s", exc)
        finally:
            stop_event.set()
            if self.daemon is not None:
                self.daemon.stop()


def run_watch_loop(
    exercise_dir: Path = Path("exercises"),
    warm_daemon: bool = True,
    **kwargs: Any,
) -> None:
    """Convenience entrypoint to initialize RayDaemon and start ExerciseWatcher loop."""
    daemon = RayDaemon() if warm_daemon else None
    watcher = ExerciseWatcher(daemon=daemon)
    watcher.watch_loop(exercise_dir=exercise_dir)
