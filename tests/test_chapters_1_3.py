"""Verification tests for Chapters 1 to 3 curriculum and reference solutions."""

from pathlib import Path

import pytest

from raylings.manifest import get_manifest
from raylings.models import Exercise
from raylings.runner import ExerciseRunner

pytestmark = pytest.mark.heavy


def get_chapter_exercises(chapter_numbers: list[int]) -> list[Exercise]:
    """Retrieve exercises belonging to specified chapter numbers."""
    manifest = get_manifest()
    exercises = []
    for ch in manifest.chapters:
        if ch.number in chapter_numbers:
            exercises.extend(ch.exercises)
    return exercises


CHAPTER_1_3_EXERCISES = get_chapter_exercises([1, 2, 3])


@pytest.mark.parametrize("exercise", CHAPTER_1_3_EXERCISES, ids=lambda ex: ex.name)
def test_exercise_file_fails_initially(exercise: Exercise):
    """Verify that every exercise file exists and fails initially."""
    runner = ExerciseRunner()
    ex_path = Path(exercise.path)
    assert ex_path.exists(), f"Exercise file missing: {ex_path}"

    result = runner.run_exercise(exercise, timeout=30.0)
    assert result.passed is False, f"Exercise {exercise.name} should fail initially until completed"


@pytest.mark.parametrize("exercise", CHAPTER_1_3_EXERCISES, ids=lambda ex: ex.name)
def test_solution_file_passes_cleanly(exercise: Exercise):
    """Verify that every reference solution exists and passes cleanly."""
    runner = ExerciseRunner()
    sol_path = exercise.solution_path
    assert sol_path.exists(), f"Solution file missing: {sol_path}"

    result = runner.run_solution(exercise, timeout=45.0)
    assert result.passed is True, (
        f"Solution {exercise.name} failed with exit_code={result.exit_code}:\n{result.error}\nOutput:\n{result.output}"
    )
    assert result.error is None
    assert result.exit_code == 0
