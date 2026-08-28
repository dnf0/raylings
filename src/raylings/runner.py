"""Exercise runner and execution evaluator for Raylings."""

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from raylings.models import Exercise

NOT_DONE_MARKER = "I AM NOT DONE"


@dataclass
class RunResult:
    """Encapsulates the execution result and evaluation state of an exercise."""

    exercise: Exercise
    passed: bool
    has_not_done_marker: bool
    output: str
    error: str | None = None
    exit_code: int = 0


class ExerciseRunner:
    """Executes exercises and canonical solutions in isolated subprocesses."""

    def check_marker(self, path: Path) -> bool:
        """Check if the given file contains the 'I AM NOT DONE' marker or unfilled blanks.

        Args:
            path: Filesystem path to the exercise file.

        Returns:
            bool: True if marker or placeholder exists in the file content, False otherwise.
        """
        if not path.exists():
            return False
        try:
            content = path.read_text(encoding="utf-8")
            has_not_done_comment = (
                "I AM NOT DONE" in content
                or "# I AM NOT DONE" in content
                or "// I AM NOT DONE" in content
                or "<!-- I AM NOT DONE -->" in content
            )
            has_unfilled_blank = (
                "___" in content
                or "/* ??? */" in content
                or "<!-- ANSWER -->" in content
            )
            return has_not_done_comment or has_unfilled_blank
        except Exception:
            return False

    def _get_execution_env(self) -> dict[str, str]:
        """Construct the execution environment with proper PYTHONPATH configured."""
        env = os.environ.copy()
        src_path = str(Path(__file__).resolve().parent.parent)
        root_path = str(Path(__file__).resolve().parent.parent.parent)
        existing_pythonpath = env.get("PYTHONPATH", "")
        paths = [root_path, src_path]
        if existing_pythonpath:
            paths.append(existing_pythonpath)
        env["PYTHONPATH"] = os.pathsep.join(paths)
        env["RAY_ACCEL_ENV_VAR_OVERRIDE_ON_ZERO"] = "0"
        env["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
        env["RAY_RUNTIME_ENV_DEFAULT_EXCLUDES"] = ".git,.venv,dist,build,.ruff_cache,.pytest_cache"
        env["RAY_OVERRIDE_RUNTIME_ENV_DEFAULT_EXCLUDES"] = (
            ".git,.venv,dist,build,.ruff_cache,.pytest_cache"
        )
        env["RAY_DASHBOARD_ENABLE"] = "0"
        env["RAY_INCLUDE_DASHBOARD"] = "0"
        env["RAY_LOG_TO_DRIVER"] = "0"
        env.pop("RAY_ADDRESS", None)
        return env

    def _execute_script(
        self,
        exercise: Exercise,
        path: Path,
        timeout: float = 30.0,
        python_exe: str | None = None,
        is_solution: bool = False,
    ) -> RunResult:
        """Execute a Python file in a subprocess and construct a RunResult.

        Args:
            exercise: Exercise model instance.
            path: Path to the python script (exercise or solution).
            timeout: Subprocess execution timeout in seconds.
            python_exe: Optional python interpreter binary path.
            is_solution: True if running reference solution.

        Returns:
            RunResult with pass/fail evaluation and output diagnostics.
        """
        label = "Solution" if is_solution else "Exercise"
        if not path.exists():
            return RunResult(
                exercise=exercise,
                passed=False,
                has_not_done_marker=False,
                output="",
                error=f"{label} file not found: {path}",
                exit_code=1,
            )

        has_marker = self.check_marker(path)
        env = self._get_execution_env()
        exe = python_exe or sys.executable

        try:
            proc = subprocess.run(
                [exe, str(path.resolve())],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
            passed = (proc.returncode == 0) and (not has_marker)
            error = proc.stderr if proc.returncode != 0 else None
            return RunResult(
                exercise=exercise,
                passed=passed,
                has_not_done_marker=has_marker,
                output=proc.stdout,
                error=error,
                exit_code=proc.returncode,
            )
        except subprocess.TimeoutExpired as e:
            stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
            stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
            return RunResult(
                exercise=exercise,
                passed=False,
                has_not_done_marker=has_marker,
                output=stdout,
                error=f"{label} execution timed out after {timeout:.1f}s.\n{stderr}".strip(),
                exit_code=124,
            )
        except Exception as exc:
            return RunResult(
                exercise=exercise,
                passed=False,
                has_not_done_marker=has_marker,
                output="",
                error=f"{label} execution failed with unexpected error: {exc}",
                exit_code=1,
            )

    def run_exercise(
        self,
        exercise: Exercise,
        timeout: float = 30.0,
        python_exe: str | None = None,
    ) -> RunResult:
        """Execute an exercise file in a subprocess and evaluate its result.

        Args:
            exercise: Exercise instance to execute.
            timeout: Maximum execution timeout in seconds.
            python_exe: Path to Python executable (defaults to sys.executable).

        Returns:
            RunResult containing execution pass/fail status, output, and diagnostics.
        """
        return self._execute_script(
            exercise=exercise,
            path=exercise.file_path,
            timeout=timeout,
            python_exe=python_exe,
            is_solution=False,
        )

    def run_solution(
        self,
        exercise: Exercise,
        timeout: float = 30.0,
        python_exe: str | None = None,
    ) -> RunResult:
        """Execute the reference solution for an exercise in a subprocess.

        Args:
            exercise: Exercise instance whose solution to execute.
            timeout: Maximum execution timeout in seconds.
            python_exe: Path to Python executable (defaults to sys.executable).

        Returns:
            RunResult containing solution pass/fail status and output.
        """
        return self._execute_script(
            exercise=exercise,
            path=exercise.solution_path,
            timeout=timeout,
            python_exe=python_exe,
            is_solution=True,
        )
