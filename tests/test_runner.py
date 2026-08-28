"""Tests for ExerciseRunner and Rich terminal UI diagnostics."""

from pathlib import Path

from rich.console import Console

from raylings.models import Chapter, Exercise, Manifest
from raylings.runner import ExerciseRunner, RunResult
from raylings.ui import (
    render_banner,
    render_cluster_status,
    render_hint,
    render_progress,
    render_result,
)


def test_runner_detects_not_done_marker(tmp_path: Path):
    ex_file = tmp_path / "ex01.py"
    ex_file.write_text(
        "# I AM NOT DONE\ndef verify():\n    pass\nif __name__ == '__main__':\n    verify()\n"
    )
    ex = Exercise("ex01", "Test Exercise", str(ex_file), "01_test")
    runner = ExerciseRunner()

    assert runner.check_marker(ex_file) is True

    res = runner.run_exercise(ex)
    assert res.passed is False
    assert res.has_not_done_marker is True
    assert res.exit_code == 0
    assert res.exercise == ex


def test_runner_executes_passing_code(tmp_path: Path):
    ex_file = tmp_path / "ex02.py"
    ex_file.write_text(
        "def verify():\n"
        "    assert 1 + 1 == 2\n"
        "    print('SUCCESS')\n"
        "if __name__ == '__main__':\n"
        "    verify()\n"
    )
    ex = Exercise("ex02", "Test Passing", str(ex_file), "01_test")
    runner = ExerciseRunner()

    assert runner.check_marker(ex_file) is False

    res = runner.run_exercise(ex)
    assert res.passed is True
    assert res.has_not_done_marker is False
    assert res.exit_code == 0
    assert res.error is None
    assert "SUCCESS" in res.output


def test_runner_handles_failing_code(tmp_path: Path):
    ex_file = tmp_path / "ex03.py"
    ex_file.write_text(
        "def verify():\n"
        "    assert 1 == 2, 'Math is broken'\n"
        "if __name__ == '__main__':\n"
        "    verify()\n"
    )
    ex = Exercise("ex03", "Test Failing", str(ex_file), "01_test")
    runner = ExerciseRunner()

    res = runner.run_exercise(ex)
    assert res.passed is False
    assert res.exit_code != 0
    assert res.error is not None
    assert "AssertionError" in res.error or "Math is broken" in res.error


def test_runner_handles_syntax_error(tmp_path: Path):
    ex_file = tmp_path / "ex04.py"
    ex_file.write_text("def invalid_syntax(\n")
    ex = Exercise("ex04", "Test Syntax Error", str(ex_file), "01_test")
    runner = ExerciseRunner()

    res = runner.run_exercise(ex)
    assert res.passed is False
    assert res.exit_code != 0
    assert res.error is not None
    assert "SyntaxError" in res.error


def test_runner_handles_timeout(tmp_path: Path):
    ex_file = tmp_path / "ex05.py"
    ex_file.write_text("import time\ntime.sleep(2.0)\n")
    ex = Exercise("ex05", "Test Timeout", str(ex_file), "01_test")
    runner = ExerciseRunner()

    res = runner.run_exercise(ex, timeout=0.1)
    assert res.passed is False
    assert res.exit_code != 0
    assert res.error is not None
    assert "timed out" in res.error.lower()


def test_runner_run_solution(tmp_path: Path):
    ex_dir = tmp_path / "exercises" / "01_basics"
    sol_dir = tmp_path / "solutions" / "01_basics"
    ex_dir.mkdir(parents=True)
    sol_dir.mkdir(parents=True)

    ex_file = ex_dir / "basics01.py"
    sol_file = sol_dir / "basics01.py"

    ex_file.write_text("# I AM NOT DONE\nassert False\n")
    sol_file.write_text("print('Solution is valid!')\nassert True\n")

    ex = Exercise(
        name="basics01",
        title="Ray Init",
        path=str(ex_file),
        chapter_name="01_basics",
    )
    runner = ExerciseRunner()

    # Solution should pass
    sol_res = runner.run_solution(ex)
    assert sol_res.passed is True
    assert sol_res.exit_code == 0
    assert sol_res.has_not_done_marker is False
    assert "Solution is valid!" in sol_res.output

    # Exercise itself should fail because of marker and assert False
    ex_res = runner.run_exercise(ex)
    assert ex_res.passed is False


def test_runner_handles_missing_file(tmp_path: Path):
    ex_file = tmp_path / "non_existent.py"
    ex = Exercise("non_existent", "Missing", str(ex_file), "01_test")
    runner = ExerciseRunner()

    res = runner.run_exercise(ex)
    assert res.passed is False
    assert res.exit_code != 0
    assert res.error is not None


def test_ui_render_banner():
    test_console = Console(record=True)
    render_banner(console=test_console)
    output = test_console.export_text()
    assert "RAYLINGS" in output


def test_ui_render_result_passed(tmp_path: Path):
    ex = Exercise("ex01", "Test Exercise", str(tmp_path / "ex01.py"), "01_test")
    result = RunResult(
        exercise=ex,
        passed=True,
        has_not_done_marker=False,
        output="All assertions passed!",
        error=None,
        exit_code=0,
    )
    test_console = Console(record=True)
    render_result(result, console=test_console)
    output = test_console.export_text()
    assert "ex01" in output
    assert "passed" in output.lower()


def test_ui_render_result_failed_marker(tmp_path: Path):
    ex = Exercise("ex01", "Test Exercise", str(tmp_path / "ex01.py"), "01_test")
    result = RunResult(
        exercise=ex,
        passed=False,
        has_not_done_marker=True,
        output="Tests succeeded but marker present",
        error=None,
        exit_code=0,
    )
    test_console = Console(record=True)
    render_result(result, console=test_console)
    output = test_console.export_text()
    assert "I AM NOT DONE" in output


def test_ui_render_result_failed_error(tmp_path: Path):
    ex = Exercise("ex01", "Test Exercise", str(tmp_path / "ex01.py"), "01_test")
    result = RunResult(
        exercise=ex,
        passed=False,
        has_not_done_marker=False,
        output="",
        error="Traceback (most recent call last):\n  File 'ex01.py', line 1\nAssertionError",
        exit_code=1,
    )
    test_console = Console(record=True)
    render_result(result, console=test_console)
    output = test_console.export_text()
    assert "Error" in output or "AssertionError" in output


def test_ui_render_prompts(tmp_path: Path):
    from raylings.ui import render_failure_prompt, render_success_prompt

    ex1 = Exercise("ex01", "Test Exercise 1", str(tmp_path / "ex01.py"), "01_test")
    ex2 = Exercise("ex02", "Test Exercise 2", str(tmp_path / "ex02.py"), "01_test")

    test_console = Console(record=True)
    render_success_prompt(ex1, next_exercise=ex2, console=test_console)
    out_succ = test_console.export_text()
    assert "ex01 passed" in out_succ
    assert "Advance to next exercise" in out_succ

    test_console = Console(record=True)
    render_failure_prompt(ex1, console=test_console)
    out_fail = test_console.export_text()
    assert "ex01 is not passing yet" in out_fail
    assert "Reveal progressive hint" in out_fail


def test_ui_render_hint(tmp_path: Path):
    ex = Exercise(
        name="ex01",
        title="Test Exercise",
        path=str(tmp_path / "ex01.py"),
        chapter_name="01_test",
        hints=["Hint 1: Check ray.init()", "Hint 2: Use ray.get()"],
    )
    test_console = Console(record=True)
    render_hint(ex, hint_level=0, console=test_console)
    out0 = test_console.export_text()
    assert "Hint 1" in out0

    test_console = Console(record=True)
    render_hint(ex, hint_level=1, console=test_console)
    out1 = test_console.export_text()
    assert "Hint 2" in out1

    # Exercise with no hints
    ex_no_hints = Exercise(
        name="ex02",
        title="No Hints",
        path=str(tmp_path / "ex02.py"),
        chapter_name="01_test",
        hints=[],
    )
    test_console = Console(record=True)
    render_hint(ex_no_hints, hint_level=0, console=test_console)
    out_none = test_console.export_text()
    assert "No hints available" in out_none


def test_ui_render_progress(tmp_path: Path):
    ex1 = Exercise("ex01", "Test 1", str(tmp_path / "ex01.py"), "01_test")
    ex2 = Exercise("ex02", "Test 2", str(tmp_path / "ex02.py"), "01_test")
    ch = Chapter(1, "01_test", "Chapter 1", "Description", [ex1, ex2])
    manifest = Manifest(chapters=[ch])

    test_console = Console(record=True)
    render_progress(manifest, completed_count=1, console=test_console)
    output = test_console.export_text()
    assert "Chapter 1" in output
    assert "Progress" in output or "1/2" in output or "50%" in output


def test_ui_render_cluster_status():
    cluster_info_running = {
        "is_running": True,
        "address": "127.0.0.1:6379",
        "node_count": 1,
        "cluster_resources": {"CPU": 4.0, "object_store_memory": 104857600.0},
        "available_resources": {"CPU": 4.0},
    }
    test_console = Console(record=True)
    render_cluster_status(cluster_info_running, console=test_console)
    out_running = test_console.export_text()
    assert "127.0.0.1:6379" in out_running
    assert "Running" in out_running or "Active" in out_running or "Node" in out_running

    cluster_info_stopped = {
        "is_running": False,
        "address": None,
        "node_count": 0,
        "cluster_resources": {},
        "available_resources": {},
    }
    test_console = Console(record=True)
    render_cluster_status(cluster_info_stopped, console=test_console)
    out_stopped = test_console.export_text()
    assert "Stopped" in out_stopped or "Inactive" in out_stopped or "Offline" in out_stopped


def test_runner_detects_placeholder_markers(tmp_path: Path):
    """Verify check_marker detects comments and blank placeholders."""
    runner = ExerciseRunner()

    # Test legacy and alternate comment formats
    for comment in ["# I AM NOT DONE", "// I AM NOT DONE", "<!-- I AM NOT DONE -->"]:
        f = tmp_path / f"test_{abs(hash(comment))}.py"
        f.write_text(f"{comment}\ndef verify(): pass\n")
        assert runner.check_marker(f) is True

    # Test cloze blank placeholders
    for placeholder in ["___", "/* ??? */", "<!-- ANSWER -->"]:
        f = tmp_path / f"test_{abs(hash(placeholder))}.py"
        f.write_text(f"x = {placeholder}\ndef verify(): pass\n")
        assert runner.check_marker(f) is True

    # Test clean file without marker
    clean_f = tmp_path / "clean.py"
    clean_f.write_text("def verify(): pass\n")
    assert runner.check_marker(clean_f) is False
