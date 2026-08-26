import pytest
from raylings.manifest import Exercise, get_manifest
from raylings.runner import ExerciseRunner


def _get_chapter_exercises(chapter_names: set[str]) -> list[Exercise]:
    manifest = get_manifest()
    exercises = []
    for ch in manifest.chapters:
        if ch.name in chapter_names:
            exercises.extend(ch.exercises)
    return exercises


CHAPTER_4_6_EXERCISES = _get_chapter_exercises(
    {
        "04_scheduling_resources",
        "05_fault_tolerance",
        "06_cluster_architecture",
    }
)


@pytest.mark.parametrize("exercise", CHAPTER_4_6_EXERCISES, ids=lambda ex: ex.name)
def test_exercise_skeleton_fails_with_marker(exercise: Exercise) -> None:
    """Verify that every exercise file exists, has the marker, and fails default run."""
    runner = ExerciseRunner()
    ex_path = exercise.file_path
    assert ex_path.exists(), f"Exercise file missing: {ex_path}"

    has_marker = runner.check_marker(ex_path)
    assert has_marker is True, f"Exercise {exercise.name} must have '# I AM NOT DONE' marker"

    result = runner.run_exercise(exercise, timeout=30.0)
    assert result.passed is False, (
        f"Exercise {exercise.name} should fail when marker is present or uncompleted"
    )


@pytest.mark.parametrize("exercise", CHAPTER_4_6_EXERCISES, ids=lambda ex: ex.name)
def test_solution_file_passes_cleanly(exercise: Exercise) -> None:
    """Verify that every reference solution exists, has no marker, and passes cleanly."""
    runner = ExerciseRunner()
    sol_path = exercise.solution_path
    assert sol_path.exists(), f"Solution file missing: {sol_path}"

    has_marker = runner.check_marker(sol_path)
    assert has_marker is False, f"Solution {sol_path} must NOT contain the '# I AM NOT DONE' marker"

    result = runner.run_solution(exercise, timeout=60.0)
    msg = f"Solution {exercise.name} failed with exit_code={result.exit_code}:\n{result.error}\nOutput:\n{result.output}"
    assert result.passed is True, msg
    assert result.error is None
    assert result.exit_code == 0
