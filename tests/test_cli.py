"""Test suite for Raylings CLI commands and the exercise file watcher loop."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from raylings.models import Chapter, Exercise, Manifest
from raylings.runner import NOT_DONE_MARKER, ExerciseRunner

runner = CliRunner()


def test_cli_version():
    """Verify version command and --version flag display version information."""
    from raylings import __version__
    from raylings.cli import app

    res_cmd = runner.invoke(app, ["version"])
    assert res_cmd.exit_code == 0
    assert __version__ in res_cmd.stdout

    res_flag = runner.invoke(app, ["--version"])
    assert res_flag.exit_code == 0
    assert __version__ in res_flag.stdout


def test_cli_list():
    """Verify list command renders chapters and exercises table."""
    import json

    from raylings.cli import app

    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "01_basics" in result.stdout or "Ray Core Foundations" in result.stdout
    assert "Curriculum Chapters" in result.stdout or "Chapter" in result.stdout

    # Test JSON output
    res_json = runner.invoke(app, ["list", "--json"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.stdout)
    assert data["total_exercises"] == 78
    assert len(data["chapters"]) == 17
    assert data["chapters"][0]["name"] == "01_basics"


def test_cli_progress():
    """Verify progress command renders summary and supports JSON output."""
    import json

    from raylings.cli import app

    res_cli = runner.invoke(app, ["progress"])
    assert res_cli.exit_code == 0

    res_json = runner.invoke(app, ["progress", "--json"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.stdout)
    assert data["total"] == 78
    assert "completed" in data
    assert "percentage" in data


def test_cli_hint():
    """Verify hint command displays progressive hints or errors on invalid names."""
    import json

    from raylings.cli import app

    # Valid exercise hint
    res_hint = runner.invoke(app, ["hint", "basics01"])
    assert res_hint.exit_code == 0
    assert "Hint" in res_hint.stdout or "hint" in res_hint.stdout.lower()

    # Hint with custom level option
    res_level = runner.invoke(app, ["hint", "basics01", "--level", "1"])
    assert res_level.exit_code == 0
    assert "Hint" in res_level.stdout or "hint" in res_level.stdout.lower()

    # Hint JSON output
    res_json = runner.invoke(app, ["hint", "basics01", "--json"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.stdout)
    assert data["name"] == "basics01"
    assert len(data["hints"]) > 0

    # Invalid exercise hint
    res_invalid = runner.invoke(app, ["hint", "nonexistent_ex_xyz_999"])
    assert res_invalid.exit_code != 0
    assert "not found" in res_invalid.stdout.lower()


def test_cli_run_exercise(tmp_path: Path):
    """Verify run command executes an exercise or script path."""
    from raylings.cli import app

    passing_file = tmp_path / "test_pass.py"
    passing_file.write_text("def test_ok(): pass\nif __name__ == '__main__': test_ok()\n")

    failing_file = tmp_path / "test_fail.py"
    failing_file.write_text(f"#{NOT_DONE_MARKER}\nraise RuntimeError('fail')\n")

    # Run passing script by path
    res_pass = runner.invoke(app, ["run", str(passing_file)])
    assert res_pass.exit_code == 0
    assert "passed" in res_pass.stdout.lower() or "SUCCESS" in res_pass.stdout

    # Run failing script by path
    res_fail = runner.invoke(app, ["run", str(failing_file)])
    assert res_fail.exit_code != 0

    # Run nonexistent exercise
    res_missing = runner.invoke(app, ["run", "completely_unknown_ex_123"])
    assert res_missing.exit_code != 0


def test_cli_daemon_status(monkeypatch: pytest.MonkeyPatch):
    """Verify daemon commands (status, start, stop, restart)."""
    import raylings.cli as cli_module
    from raylings.cli import app

    mock_daemon = MagicMock()
    mock_daemon.get_cluster_info.return_value = {
        "is_running": True,
        "address": "127.0.0.1:6379",
        "node_count": 1,
        "cluster_resources": {"CPU": 2.0},
        "available_resources": {"CPU": 2.0},
    }
    monkeypatch.setattr(cli_module, "RayDaemon", lambda *args, **kwargs: mock_daemon)

    res_status = runner.invoke(app, ["daemon", "status"])
    assert res_status.exit_code == 0

    res_start = runner.invoke(app, ["daemon", "start"])
    assert res_start.exit_code == 0
    assert mock_daemon.start.called

    res_stop = runner.invoke(app, ["daemon", "stop"])
    assert res_stop.exit_code == 0
    assert mock_daemon.stop.called

    res_restart = runner.invoke(app, ["daemon", "restart"])
    assert res_restart.exit_code == 0

    res_invalid = runner.invoke(app, ["daemon", "invalid_action_xyz"])
    assert res_invalid.exit_code != 0


def test_cli_test_solutions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Verify test command executes solution files and produces summary reports."""
    import raylings.cli as cli_module
    from raylings.cli import app

    # Create mock solution files
    sol1 = tmp_path / "sol1.py"
    sol1.write_text("if __name__ == '__main__': pass\n")
    sol2 = tmp_path / "sol2.py"
    sol2.write_text("if __name__ == '__main__': pass\n")

    ex1 = Exercise(name="mock01", title="Mock 1", path=str(sol1), chapter_name="01_test")
    ex2 = Exercise(name="mock02", title="Mock 2", path=str(sol2), chapter_name="01_test")
    mock_manifest = Manifest(
        chapters=[
            Chapter(
                number=1,
                name="01_test",
                title="Test Chapter",
                description="Test",
                exercises=[ex1, ex2],
            )
        ]
    )

    monkeypatch.setattr(cli_module, "get_manifest", lambda: mock_manifest)
    monkeypatch.setattr(
        cli_module, "get_exercise_by_name", lambda name: ex1 if name == "mock01" else None
    )

    # Test single exercise solution
    res_single = runner.invoke(app, ["test", "mock01"])
    assert res_single.exit_code == 0
    assert "passed" in res_single.stdout.lower() or "SUCCESS" in res_single.stdout

    # Test all solutions with summary
    res_all = runner.invoke(app, ["test", "--all"])
    assert res_all.exit_code == 0
    assert (
        "2 passed" in res_all.stdout.lower()
        or "All" in res_all.stdout
        or "passed" in res_all.stdout.lower()
    )

    # Test missing solution
    res_missing = runner.invoke(app, ["test", "nonexistent_sol"])
    assert res_missing.exit_code != 0


def test_watcher_find_current_exercise(tmp_path: Path):
    """Verify ExerciseWatcher locates the first pending or incomplete exercise in manifest order."""
    from raylings.watcher import ExerciseWatcher

    # ex1: passed cleanly
    ex1_file = tmp_path / "ex01.py"
    ex1_file.write_text("if __name__ == '__main__': pass\n")

    # ex2: fails validation (assert False)
    ex2_file = tmp_path / "ex02.py"
    ex2_file.write_text("assert False, 'Not solved yet'\n")

    # ex3: fails validation
    ex3_file = tmp_path / "ex03.py"
    ex3_file.write_text("assert False, 'Not solved yet'\n")

    ex1 = Exercise(name="ex01", title="Ex 1", path=str(ex1_file), chapter_name="01_test")
    ex2 = Exercise(name="ex02", title="Ex 2", path=str(ex2_file), chapter_name="01_test")
    ex3 = Exercise(name="ex03", title="Ex 3", path=str(ex3_file), chapter_name="01_test")

    manifest = Manifest(
        chapters=[
            Chapter(
                number=1,
                name="01_test",
                title="Test",
                description="Test",
                exercises=[ex1, ex2, ex3],
            )
        ]
    )

    from raylings.state import StateTracker

    watcher = ExerciseWatcher(
        manifest=manifest,
        runner=ExerciseRunner(),
        tracker=StateTracker(root_dir=tmp_path),
    )
    current = watcher.find_current_exercise()
    assert current is not None
    assert current.name == "ex02"

    # Fix ex2
    ex2_file.write_text("if __name__ == '__main__': pass\n")
    next_current = watcher.find_current_exercise()
    assert next_current is not None
    assert next_current.name == "ex03"

    # Fix ex3
    ex3_file.write_text("if __name__ == '__main__': pass\n")
    all_done = watcher.find_current_exercise()
    assert all_done is None


def test_watcher_handle_change(tmp_path: Path):
    """Verify ExerciseWatcher.on_file_changed correctly processes modifications to exercise files."""
    from raylings.watcher import ExerciseWatcher

    ex_file = tmp_path / "ex_change.py"
    ex_file.write_text("assert False, 'Initial failing state'\n")

    ex = Exercise(name="ex_change", title="Ex Change", path=str(ex_file), chapter_name="01_test")
    manifest = Manifest(
        chapters=[
            Chapter(number=1, name="01_test", title="Test", description="Test", exercises=[ex])
        ]
    )

    watcher = ExerciseWatcher(manifest=manifest, runner=ExerciseRunner())

    # File fails validation
    res = watcher.on_file_changed(ex_file)
    assert res is not None
    assert not res.passed

    # Fix code and re-trigger
    ex_file.write_text("if __name__ == '__main__': pass\n")
    res_passed = watcher.on_file_changed(ex_file)
    assert res_passed is not None
    assert res_passed.passed

    # Modify unrelated file
    unknown_file = tmp_path / "unrelated.py"
    unknown_file.write_text("print('hello')\n")
    assert watcher.on_file_changed(unknown_file) is None


def test_watcher_watch_loop_graceful_exit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Verify watch_loop handles KeyboardInterrupt gracefully and stops daemon."""
    from raylings.watcher import ExerciseWatcher

    mock_daemon = MagicMock()
    watcher = ExerciseWatcher(
        manifest=Manifest(chapters=[]), runner=ExerciseRunner(), daemon=mock_daemon
    )

    def mock_watch(*args, **kwargs):
        raise KeyboardInterrupt()

    monkeypatch.setattr("watchfiles.watch", mock_watch)

    # Should not raise exception
    watcher.watch_loop(exercise_dir=tmp_path)
    mock_daemon.stop.assert_called()


def test_cli_init(tmp_path: Path):
    """Verify init command creates an exercises directory with exercise files."""
    from raylings.cli import app

    target_dir = tmp_path / "my_learning_space"
    target_dir.mkdir()

    res = runner.invoke(app, ["init", "--directory", str(target_dir)])
    assert res.exit_code == 0
    assert "initialized successfully" in res.stdout

    exercises_dir = target_dir / "exercises"
    assert exercises_dir.exists()
    assert (exercises_dir / "01_basics" / "basics01.py").exists()

    # Re-running without --force should warn but exit cleanly
    res_rerun = runner.invoke(app, ["init", "--directory", str(target_dir)])
    assert res_rerun.exit_code == 0
    assert "already exists" in res_rerun.stdout


def test_cli_tour_json():
    """Verify tour --json outputs structured tour JSON metadata."""
    import json

    from raylings.cli import app

    res = runner.invoke(app, ["tour", "--json"])
    assert res.exit_code == 0
    data = json.loads(res.stdout)
    assert "title" in data
    assert "total_steps" in data
    assert data["total_steps"] == 5
    assert len(data["steps"]) == 5
    assert data["steps"][0]["step_number"] == 1
    assert "Welcome" in data["steps"][0]["title"]
    assert data["steps"][4]["step_number"] == 5
    assert "VS Code" in data["steps"][4]["title"]


def test_cli_tour_step_valid():
    """Verify tour --step <N> renders only the requested step."""
    from raylings.cli import app

    res = runner.invoke(app, ["tour", "--step", "3"])
    assert res.exit_code == 0
    assert "Step 3/5" in res.stdout or "3/5" in res.stdout
    assert "basics01" in res.stdout or "First Exercise" in res.stdout
    assert "Step 1/5" not in res.stdout


def test_cli_tour_step_invalid():
    """Verify tour --step with out-of-bounds number produces error."""
    from raylings.cli import app

    res_high = runner.invoke(app, ["tour", "--step", "99"])
    assert res_high.exit_code != 0
    assert (
        "Invalid step" in res_high.stdout
        or "between 1 and 5" in res_high.stdout
        or "not found" in res_high.stdout.lower()
    )

    res_low = runner.invoke(app, ["tour", "--step", "0"])
    assert res_low.exit_code != 0


def test_cli_tour_non_interactive():
    """Verify tour --non-interactive renders all 5 steps sequentially."""
    from raylings.cli import app

    res = runner.invoke(app, ["tour", "--non-interactive"])
    assert res.exit_code == 0
    assert "Step 1/5" in res.stdout or "1/5" in res.stdout
    assert "Step 2/5" in res.stdout or "2/5" in res.stdout
    assert "Step 3/5" in res.stdout or "3/5" in res.stdout
    assert "Step 4/5" in res.stdout or "4/5" in res.stdout
    assert "Step 5/5" in res.stdout or "5/5" in res.stdout


def test_cli_doctor_text():
    """Verify doctor command runs preflight diagnostic checks and renders rich table."""
    from raylings.cli import app

    res = runner.invoke(app, ["doctor"])
    assert res.exit_code == 0
    assert (
        "Preflight Diagnostics" in res.stdout
        or "Diagnostics" in res.stdout
        or "Doctor" in res.stdout
    )
    assert "Python" in res.stdout
    assert "Ray" in res.stdout
    assert "PASS" in res.stdout or "✓" in res.stdout


def test_cli_doctor_json():
    """Verify doctor --json returns structured diagnostic results."""
    import json

    from raylings.cli import app

    res = runner.invoke(app, ["doctor", "--json"])
    assert res.exit_code == 0
    data = json.loads(res.stdout)
    assert "status" in data
    assert "checks" in data
    assert isinstance(data["checks"], list)
    assert len(data["checks"]) >= 5
    check_names = [c["name"].lower() for c in data["checks"]]
    assert any("python" in name for name in check_names)
    assert any("ray" in name for name in check_names)
    assert any("daemon" in name or "cluster" in name for name in check_names)
    assert any("exercises" in name for name in check_names)
    assert any("cpu" in name or "system" in name for name in check_names)


def test_cli_tour_interactive_quit(monkeypatch: pytest.MonkeyPatch):
    """Verify interactive tour exits cleanly when user inputs 'q'."""
    import typer.testing

    from raylings.cli import app

    monkeypatch.setattr(typer.testing._NamedTextIOWrapper, "isatty", lambda self: True)
    res = runner.invoke(app, ["tour"], input="q\n")
    assert res.exit_code == 0
    assert "Step 1/5" in res.stdout or "1/5" in res.stdout
    assert "Step 2/5" not in res.stdout


def test_cli_tour_interactive_complete(monkeypatch: pytest.MonkeyPatch):
    """Verify interactive tour steps through all steps on Enter."""
    import typer.testing

    from raylings.cli import app

    monkeypatch.setattr(typer.testing._NamedTextIOWrapper, "isatty", lambda self: True)
    res = runner.invoke(app, ["tour"], input="\n\n\n\n\n")
    assert res.exit_code == 0
    assert "Step 1/5" in res.stdout or "1/5" in res.stdout
    assert "Step 5/5" in res.stdout or "5/5" in res.stdout


def test_cli_doctor_critical_failure(monkeypatch: pytest.MonkeyPatch):
    """Verify doctor returns exit code 1 if critical check (e.g. Python < 3.10) fails."""
    import sys

    from raylings.cli import app

    # Mock python version info to (3, 9, 0)
    monkeypatch.setattr(sys, "version_info", (3, 9, 0, "final", 0))

    res = runner.invoke(app, ["doctor"])
    assert res.exit_code == 1
    assert "FAIL" in res.stdout or "3.9" in res.stdout or "unsupported" in res.stdout.lower()

    res_json = runner.invoke(app, ["doctor", "--json"])
    assert res_json.exit_code == 1


def test_cli_tui_non_interactive():
    """Verify tui --non-interactive renders snapshot and exits cleanly."""
    from raylings.cli import app

    res = runner.invoke(app, ["tui", "--non-interactive"])
    assert res.exit_code == 0
    assert "basics01" in res.stdout or "Curriculum" in res.stdout

    # With pre-selected exercise
    res_ex = runner.invoke(app, ["tui", "--non-interactive", "--exercise", "basics02"])
    assert res_ex.exit_code == 0
    assert "basics02" in res_ex.stdout

    # With invalid exercise
    res_invalid = runner.invoke(app, ["tui", "--non-interactive", "--exercise", "invalid_ex_000"])
    assert res_invalid.exit_code != 0
    assert "not found" in res_invalid.stdout.lower()
