"""Unit tests for the Interactive Full-Screen Split-Pane TUI (tui.py and raylings tui command)."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from rich.console import Console
from rich.layout import Layout
from typer.testing import CliRunner

from raylings.cli import app
from raylings.metrics import ClusterSnapshot, NodeMetrics, ObjectStoreMetrics, TaskMetrics
from raylings.models import Chapter, Exercise, Manifest
from raylings.runner import ExerciseRunner, RunResult
from raylings.state import StateTracker
from raylings.tui import (
    RaylingsTUI,
    TUIAction,
    TUIState,
    TUIViewMode,
    create_tui_layout,
    handle_key,
)

cli_runner = CliRunner()


@pytest.fixture
def sample_manifest() -> Manifest:
    """Create a minimal sample manifest for testing."""
    return Manifest(
        chapters=[
            Chapter(
                number=1,
                name="01_basics",
                title="Ray Core Foundations",
                description="Tasks, Futures, and Asynchronous Execution",
                exercises=[
                    Exercise(
                        name="basics01",
                        title="Ray Init & First Remote Task",
                        path="exercises/01_basics/basics01.py",
                        chapter_name="01_basics",
                        hints=["Hint 1 for basics01", "Hint 2 for basics01"],
                    ),
                    Exercise(
                        name="basics02",
                        title="ObjectRefs and ray.get()",
                        path="exercises/01_basics/basics02.py",
                        chapter_name="01_basics",
                        hints=["Hint 1 for basics02"],
                    ),
                ],
            ),
            Chapter(
                number=2,
                name="02_actors",
                title="Distributed State & Actors",
                description="Stateful actors and method calls",
                exercises=[
                    Exercise(
                        name="actors01",
                        title="Stateful Actor Lifecycle",
                        path="exercises/02_actors/actors01.py",
                        chapter_name="02_actors",
                        hints=[],
                    ),
                ],
            ),
        ]
    )


@pytest.fixture
def temp_tracker(tmp_path: Path) -> StateTracker:
    """Create a StateTracker with isolated temporary state file."""
    return StateTracker(root_dir=tmp_path)


def test_tui_state_initialization(sample_manifest: Manifest, temp_tracker: StateTracker) -> None:
    """Verify TUIState initializes with correct defaults and pointers."""
    state = TUIState(manifest=sample_manifest, tracker=temp_tracker)

    assert state.current_exercise_idx == 0
    assert state.current_exercise is not None
    assert state.current_exercise.name == "basics01"
    assert state.current_chapter is not None
    assert state.current_chapter.name == "01_basics"
    assert state.view_mode == TUIViewMode.EXERCISE
    assert state.hint_level == 0
    assert state.show_hint is False
    assert state.last_run_result is None
    assert len(state.results_by_name) == 0


def test_tui_state_navigation(sample_manifest: Manifest, temp_tracker: StateTracker) -> None:
    """Verify forward and backward navigation and bounds clamping."""
    state = TUIState(manifest=sample_manifest, tracker=temp_tracker)
    total_exercises = len(sample_manifest.all_exercises)  # 3 exercises

    # Move next
    ex2 = state.next_exercise()
    assert ex2 is not None
    assert ex2.name == "basics02"
    assert state.current_exercise_idx == 1

    # Move next to chapter 2
    ex3 = state.next_exercise()
    assert ex3 is not None
    assert ex3.name == "actors01"
    assert state.current_exercise_idx == 2
    assert state.current_chapter is not None
    assert state.current_chapter.name == "02_actors"

    # Clamped at end
    ex_end = state.next_exercise()
    assert ex_end is not None
    assert ex_end.name == "actors01"
    assert state.current_exercise_idx == total_exercises - 1

    # Move prev
    ex_prev = state.prev_exercise()
    assert ex_prev is not None
    assert ex_prev.name == "basics02"
    assert state.current_exercise_idx == 1

    # Move prev to beginning
    state.prev_exercise()
    assert state.current_exercise_idx == 0

    # Clamped at beginning
    state.prev_exercise()
    assert state.current_exercise_idx == 0


def test_tui_state_select_by_name(sample_manifest: Manifest, temp_tracker: StateTracker) -> None:
    """Verify selecting exercise by name jumps to the correct index."""
    state = TUIState(manifest=sample_manifest, tracker=temp_tracker)

    found = state.select_exercise_by_name("actors01")
    assert found is True
    assert state.current_exercise is not None
    assert state.current_exercise.name == "actors01"
    assert state.current_exercise_idx == 2

    not_found = state.select_exercise_by_name("nonexistent")
    assert not_found is False
    assert state.current_exercise_idx == 2


def test_tui_state_hint_cycling(sample_manifest: Manifest, temp_tracker: StateTracker) -> None:
    """Verify toggling hints cycles through available hints and resets on exercise change."""
    state = TUIState(manifest=sample_manifest, tracker=temp_tracker)
    # basics01 has 2 hints

    assert state.show_hint is False
    assert state.hint_level == 0

    # First toggle: show hint 0
    lvl1 = state.toggle_hint()
    assert state.show_hint is True
    assert lvl1 == 0
    assert state.hint_level == 0

    # Second toggle: show hint 1
    lvl2 = state.toggle_hint()
    assert lvl2 == 1
    assert state.hint_level == 1

    # Third toggle: wraps back to 0
    lvl3 = state.toggle_hint()
    assert lvl3 == 0
    assert state.hint_level == 0

    # Moving to next exercise resets hints
    state.next_exercise()
    assert state.show_hint is False
    assert state.hint_level == 0

    # Exercise with 0 hints (actors01)
    state.select_exercise_by_name("actors01")
    lvl_none = state.toggle_hint()
    assert lvl_none == 0
    assert state.show_hint is True


def test_tui_state_view_modes(sample_manifest: Manifest, temp_tracker: StateTracker) -> None:
    """Verify toggling view modes between exercise, telemetry, and doctor."""
    state = TUIState(manifest=sample_manifest, tracker=temp_tracker)
    assert state.view_mode == TUIViewMode.EXERCISE

    # Toggle telemetry
    mode1 = state.toggle_telemetry()
    assert mode1 == TUIViewMode.TELEMETRY
    assert state.view_mode == TUIViewMode.TELEMETRY

    mode2 = state.toggle_telemetry()
    assert mode2 == TUIViewMode.EXERCISE
    assert state.view_mode == TUIViewMode.EXERCISE

    # Toggle doctor
    mode_doc1 = state.toggle_doctor()
    assert mode_doc1 == TUIViewMode.DOCTOR
    assert state.view_mode == TUIViewMode.DOCTOR

    mode_doc2 = state.toggle_doctor()
    assert mode_doc2 == TUIViewMode.EXERCISE
    assert state.view_mode == TUIViewMode.EXERCISE

    # Toggle telemetry from doctor
    state.toggle_doctor()
    assert state.view_mode == TUIViewMode.DOCTOR
    state.toggle_telemetry()
    assert state.view_mode == TUIViewMode.TELEMETRY


def test_tui_state_record_run_result(sample_manifest: Manifest, temp_tracker: StateTracker) -> None:
    """Verify recording run results updates state and persistence tracker."""
    state = TUIState(manifest=sample_manifest, tracker=temp_tracker)
    ex = sample_manifest.all_exercises[0]

    result_pass = RunResult(
        exercise=ex,
        passed=True,
        has_not_done_marker=False,
        output="Execution successful!",
        error=None,
        exit_code=0,
    )
    state.record_run_result(result_pass)

    assert state.last_run_result == result_pass
    assert state.results_by_name[ex.name] == result_pass
    assert temp_tracker.is_completed(ex.name) is True

    # Record failed result
    result_fail = RunResult(
        exercise=ex,
        passed=False,
        has_not_done_marker=True,
        output="",
        error="AssertionError: failed",
        exit_code=1,
    )
    state.record_run_result(result_fail)
    assert state.last_run_result == result_fail
    assert state.results_by_name[ex.name] == result_fail
    assert temp_tracker.is_completed(ex.name) is False


def test_create_tui_layout_exercise_mode(
    sample_manifest: Manifest, temp_tracker: StateTracker, tmp_path: Path
) -> None:
    """Verify Rich Layout structure and panels in EXERCISE mode."""
    # Create dummy exercise file
    ex_file = tmp_path / "exercises" / "01_basics" / "basics01.py"
    ex_file.parent.mkdir(parents=True, exist_ok=True)
    ex_file.write_text("# Ray Exercise Code\nimport ray\n")

    sample_manifest.all_exercises[0].path = str(ex_file)
    state = TUIState(manifest=sample_manifest, tracker=temp_tracker)

    layout = create_tui_layout(state)
    assert isinstance(layout, Layout)

    # Render layout to verify no rendering exceptions
    console = Console(width=120, height=40, record=True)
    console.print(layout)
    output = console.export_text()

    assert "Ray Core Foundations" in output or "Curriculum" in output
    assert "basics01" in output
    assert "basics02" in output
    assert "Output" in output or "Diagnostics" in output
    assert "Keybindings" in output or "Next" in output


def test_create_tui_layout_with_run_result(
    sample_manifest: Manifest, temp_tracker: StateTracker
) -> None:
    """Verify Output panel renders passed/failed run results properly."""
    state = TUIState(manifest=sample_manifest, tracker=temp_tracker)
    ex = sample_manifest.all_exercises[0]

    state.record_run_result(
        RunResult(
            exercise=ex,
            passed=True,
            has_not_done_marker=False,
            output="[Ray] Successfully computed 42",
            error=None,
            exit_code=0,
        )
    )

    layout = create_tui_layout(state)
    console = Console(width=120, height=40, record=True)
    console.print(layout)
    output = console.export_text()

    assert "PASSED" in output or "✓" in output
    assert "Successfully computed 42" in output


def test_create_tui_layout_with_hint_active(
    sample_manifest: Manifest, temp_tracker: StateTracker
) -> None:
    """Verify Output panel renders active hint when toggled."""
    state = TUIState(manifest=sample_manifest, tracker=temp_tracker)
    state.toggle_hint()  # Shows hint 0: "Hint 1 for basics01"

    layout = create_tui_layout(state)
    console = Console(width=120, height=40, record=True)
    console.print(layout)
    output = console.export_text()

    assert "Hint 1 for basics01" in output


def test_create_tui_layout_telemetry_mode(
    sample_manifest: Manifest, temp_tracker: StateTracker
) -> None:
    """Verify Telemetry overlay renders cluster metrics."""
    state = TUIState(manifest=sample_manifest, tracker=temp_tracker)
    state.toggle_telemetry()

    snap = ClusterSnapshot(
        is_active=True,
        ray_version="2.43.0",
        python_version="3.12.9",
        cluster_address="127.0.0.1:6379",
        total_cpus=8.0,
        used_cpus=2.0,
        nodes=[
            NodeMetrics(
                node_id="node-1",
                node_ip="127.0.0.1",
                is_head_node=True,
                cpu_cores_total=8.0,
                cpu_cores_used=2.0,
                cpu_percent=25.0,
            )
        ],
        object_store=ObjectStoreMetrics(total_bytes=1024**3, used_bytes=0),
        tasks=TaskMetrics(),
    )

    layout = create_tui_layout(state, metrics_snapshot=snap)
    console = Console(width=120, height=40, record=True)
    console.print(layout)
    output = console.export_text()

    assert "Telemetry" in output or "Cluster" in output
    assert "127.0.0.1" in output


def test_create_tui_layout_doctor_mode(
    sample_manifest: Manifest, temp_tracker: StateTracker
) -> None:
    """Verify Doctor overlay renders diagnostic checks."""
    state = TUIState(manifest=sample_manifest, tracker=temp_tracker)
    state.toggle_doctor()

    checks = [
        {
            "name": "Python Version",
            "status": "pass",
            "critical": True,
            "details": "Python 3.12.9 (>= 3.10 supported)",
        },
        {
            "name": "Ray Installation",
            "status": "pass",
            "critical": True,
            "details": "Ray v2.43.0 installed",
        },
    ]

    layout = create_tui_layout(state, doctor_checks=checks)
    console = Console(width=120, height=40, record=True)
    console.print(layout)
    output = console.export_text()

    assert "Diagnostics" in output or "Doctor" in output
    assert "Python Version" in output


def test_handle_key_navigation_and_features(
    sample_manifest: Manifest, temp_tracker: StateTracker
) -> None:
    """Verify key event handler dispatches appropriate TUI actions."""
    state = TUIState(manifest=sample_manifest, tracker=temp_tracker)

    # Next exercise keys: 'j', 'down', 'n'
    assert handle_key("j", state) == TUIAction.NEXT
    assert state.current_exercise_idx == 1
    assert handle_key("down", state) == TUIAction.NEXT
    assert state.current_exercise_idx == 2
    assert handle_key("n", state) == TUIAction.NEXT

    # Prev exercise keys: 'k', 'up', 'p'
    assert handle_key("k", state) == TUIAction.PREV
    assert state.current_exercise_idx == 1
    assert handle_key("up", state) == TUIAction.PREV
    assert state.current_exercise_idx == 0
    assert handle_key("p", state) == TUIAction.PREV

    # Run key: 'r'
    assert handle_key("r", state) == TUIAction.RUN

    # Hint key: 'h'
    assert handle_key("h", state) == TUIAction.HINT
    assert state.show_hint is True

    # Telemetry key: 't'
    assert handle_key("t", state) == TUIAction.TELEMETRY
    assert state.view_mode == TUIViewMode.TELEMETRY

    # Escape resets view mode
    assert handle_key("escape", state) == TUIAction.NONE
    assert state.view_mode == TUIViewMode.EXERCISE

    # Doctor key: 'd'
    assert handle_key("d", state) == TUIAction.DOCTOR
    assert state.view_mode == TUIViewMode.DOCTOR
    assert handle_key("d", state) == TUIAction.DOCTOR
    assert state.view_mode == TUIViewMode.EXERCISE

    # Quit key: 'q'
    assert handle_key("q", state) == TUIAction.QUIT
    assert handle_key("Q", state) == TUIAction.QUIT

    # Unrecognized key
    assert handle_key("z", state) == TUIAction.NONE


def test_raylings_tui_run_current_exercise(
    sample_manifest: Manifest, temp_tracker: StateTracker
) -> None:
    """Verify RaylingsTUI executes runner and records results."""
    mock_runner = MagicMock(spec=ExerciseRunner)
    ex = sample_manifest.all_exercises[0]
    expected_res = RunResult(
        exercise=ex,
        passed=True,
        has_not_done_marker=False,
        output="Runner OK",
        error=None,
        exit_code=0,
    )
    mock_runner.run_exercise.return_value = expected_res

    tui = RaylingsTUI(
        manifest=sample_manifest,
        runner=mock_runner,
        tracker=temp_tracker,
    )

    res = tui.run_current_exercise()
    assert res == expected_res
    mock_runner.run_exercise.assert_called_once_with(ex)
    assert tui.state.last_run_result == expected_res
    assert temp_tracker.is_completed(ex.name) is True


def test_raylings_tui_render_once(sample_manifest: Manifest, temp_tracker: StateTracker) -> None:
    """Verify render_once outputs the layout non-interactively."""
    console = Console(record=True, width=120, height=40)
    tui = RaylingsTUI(
        manifest=sample_manifest,
        tracker=temp_tracker,
        console=console,
    )

    tui.render_once(exercise_name="basics02")
    output = console.export_text()

    assert tui.state.current_exercise is not None
    assert tui.state.current_exercise.name == "basics02"
    assert "basics02" in output


def test_cli_tui_command_non_interactive() -> None:
    """Verify raylings tui CLI command with --non-interactive and --exercise flags."""
    # 1. Non-interactive default
    result = cli_runner.invoke(app, ["tui", "--non-interactive"])
    assert result.exit_code == 0
    assert "basics01" in result.output or "Curriculum" in result.output

    # 2. Non-interactive with specific exercise
    result_ex = cli_runner.invoke(app, ["tui", "--non-interactive", "-e", "basics02"])
    assert result_ex.exit_code == 0
    assert "basics02" in result_ex.output

    # 3. Non-interactive with invalid exercise
    result_err = cli_runner.invoke(app, ["tui", "--non-interactive", "-e", "nonexistent_ex_999"])
    assert result_err.exit_code != 0
    assert "not found" in result_err.output.lower()
