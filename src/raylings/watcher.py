"""File watcher loop and interactive exercise evaluator."""

import logging
from pathlib import Path
from typing import Any

from raylings.daemon import RayDaemon
from raylings.manifest import get_manifest
from raylings.models import Exercise, Manifest
from raylings.runner import ExerciseRunner, RunResult
from raylings.ui import console, render_banner, render_result

logger = logging.getLogger("raylings.watcher")


class ExerciseWatcher:
    """Monitors exercise file modifications and coordinates interactive evaluation."""

    def __init__(
        self,
        manifest: Manifest | None = None,
        runner: ExerciseRunner | None = None,
        daemon: RayDaemon | None = None,
    ) -> None:
        """Initialize the ExerciseWatcher.

        Args:
            manifest: Optional curriculum Manifest instance (defaults to get_manifest()).
            runner: Optional ExerciseRunner instance.
            daemon: Optional RayDaemon session manager.
        """
        self.manifest = manifest if manifest is not None else get_manifest()
        self.runner = runner if runner is not None else ExerciseRunner()
        self.daemon = daemon
        self._current_exercise: Exercise | None = None

    def find_current_exercise(self) -> Exercise | None:
        """Scan curriculum exercises in order and locate the first incomplete exercise.

        An exercise is considered incomplete if its file does not exist, contains the
        'I AM NOT DONE' marker, or fails during subprocess execution.

        Returns:
            Exercise instance if an incomplete exercise is found, or None if all are completed.
        """
        for ex in self.manifest.all_exercises:
            path = ex.file_path
            if not path.exists() or self.runner.check_marker(path):
                self._current_exercise = ex
                return ex

            res = self.runner.run_exercise(ex)
            if not res.passed:
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
        render_result(res)
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
            if resolved_ex == resolved_target or file_path.name == ex.file_path.name or str(file_path).endswith(ex.path):
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

        curr = self.find_current_exercise()
        if curr is None:
            console.print(
                "[bold green]🎉 All Raylings exercises completed! Great work![/bold green]\n"
            )
        else:
            console.print(
                f"[bold cyan]Current exercise:[/bold cyan] [bold yellow]{curr.name}[/bold yellow] ({curr.title})\n"
            )
            self.evaluate_exercise(curr)

        console.print(
            f"\n[dim]👀 Watching for file changes in '{exercise_dir}'... (Press Ctrl+C to exit)[/dim]\n"
        )

        try:
            import watchfiles

            for changes in watchfiles.watch(exercise_dir):
                for _change_type, path_str in changes:
                    path = Path(path_str)
                    if path.suffix == ".py":
                        res = self.on_file_changed(path)
                        if res is not None and res.passed:
                            next_ex = self.find_current_exercise()
                            if next_ex is not None and next_ex != curr:
                                curr = next_ex
                                console.print(
                                    f"\n[bold green]Advancing to next exercise:[/bold green] "
                                    f"[cyan]{next_ex.name}[/cyan] ({next_ex.title})"
                                )
                                self.evaluate_exercise(next_ex)
                            elif next_ex is None:
                                console.print(
                                    "\n[bold green]🎉 Congratulations! You have completed all Raylings exercises![/bold green]\n"
                                )
        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting Raylings watch mode. Keep learning![/yellow]")
        except Exception as exc:
            logger.error("Error encountered during watch loop: %s", exc)
        finally:
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
