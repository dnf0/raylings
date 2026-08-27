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
    from raylings.cli import app

    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "01_basics" in result.stdout or "Ray Core Foundations" in result.stdout
    assert "Curriculum Chapters" in result.stdout or "Chapter" in result.stdout


def test_cli_hint():
    """Verify hint command displays progressive hints or errors on invalid names."""
    from raylings.cli import app

    # Valid exercise hint
    res_hint = runner.invoke(app, ["hint", "basics01"])
    assert res_hint.exit_code == 0
    assert "Hint" in res_hint.stdout or "hint" in res_hint.stdout.lower()

    # Hint with custom level option
    res_level = runner.invoke(app, ["hint", "basics01", "--level", "1"])
    assert res_level.exit_code == 0
    assert "Hint" in res_level.stdout or "hint" in res_level.stdout.lower()

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


def test_cli_daemon_status():
    """Verify daemon commands (status, start, stop, restart)."""
    from raylings.cli import app

    res_status = runner.invoke(app, ["daemon", "status"])
    assert res_status.exit_code == 0

    res_start = runner.invoke(app, ["daemon", "start"])
    assert res_start.exit_code == 0

    res_stop = runner.invoke(app, ["daemon", "stop"])
    assert res_stop.exit_code == 0

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

    # ex1: passed and no marker
    ex1_file = tmp_path / "ex01.py"
    ex1_file.write_text("if __name__ == '__main__': pass\n")

    # ex2: contains NOT_DONE_MARKER
    ex2_file = tmp_path / "ex02.py"
    ex2_file.write_text(f"#{NOT_DONE_MARKER}\nif __name__ == '__main__': pass\n")

    # ex3: contains NOT_DONE_MARKER
    ex3_file = tmp_path / "ex03.py"
    ex3_file.write_text(f"#{NOT_DONE_MARKER}\nif __name__ == '__main__': pass\n")

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

    watcher = ExerciseWatcher(manifest=manifest, runner=ExerciseRunner())
    current = watcher.find_current_exercise()
    assert current is not None
    assert current.name == "ex02"

    # Fix ex2 by removing marker
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
    ex_file.write_text(f"#{NOT_DONE_MARKER}\nif __name__ == '__main__': pass\n")

    ex = Exercise(name="ex_change", title="Ex Change", path=str(ex_file), chapter_name="01_test")
    manifest = Manifest(
        chapters=[
            Chapter(number=1, name="01_test", title="Test", description="Test", exercises=[ex])
        ]
    )

    watcher = ExerciseWatcher(manifest=manifest, runner=ExerciseRunner())

    # File has NOT_DONE marker
    res = watcher.on_file_changed(ex_file)
    assert res is not None
    assert not res.passed
    assert res.has_not_done_marker

    # Remove marker and re-trigger
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
