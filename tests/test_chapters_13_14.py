"""Test suite for Chapters 13 and 14 (Observability & KubeRay).

Verifies:
1. Exercise skeletons exist and fail initially.
2. Reference solutions exist and pass cleanly.
"""

import pytest

from raylings.manifest import get_manifest
from raylings.models import Exercise
from raylings.runner import ExerciseRunner

pytestmark = pytest.mark.heavy


MANIFEST = get_manifest()

CHAPTER_13_14_EXERCISES = [
    ex
    for ex in MANIFEST.all_exercises
    if ex.chapter_name in ["13_observability_and_debugging", "14_kuberay"]
]


def test_chapter_13_14_exercise_count() -> None:
    """Verify that Chapters 13 and 14 contain 8 exercises in total."""
    assert len(CHAPTER_13_14_EXERCISES) == 8, (
        f"Expected 8 exercises for Ch 13-14, found {len(CHAPTER_13_14_EXERCISES)}"
    )


@pytest.mark.parametrize("exercise", CHAPTER_13_14_EXERCISES, ids=lambda ex: ex.name)
def test_exercise_skeleton_fails_initially(exercise: Exercise) -> None:
    """Verify that every exercise skeleton exists and fails initially."""
    runner = ExerciseRunner()
    ex_path = exercise.file_path
    assert ex_path.exists(), f"Exercise file missing: {ex_path}"

    result = runner.run_exercise(exercise, timeout=30.0)
    assert result.passed is False, f"Exercise skeleton {exercise.name} should fail initially"


@pytest.mark.parametrize("exercise", CHAPTER_13_14_EXERCISES, ids=lambda ex: ex.name)
def test_solution_file_passes_cleanly(exercise: Exercise) -> None:
    """Verify that every reference solution exists and passes cleanly."""
    runner = ExerciseRunner()
    sol_path = exercise.solution_path
    assert sol_path.exists(), f"Solution file missing: {sol_path}"

    result = runner.run_solution(exercise, timeout=60.0)
    assert result.passed is True, (
        f"Solution {exercise.name} failed with exit_code={result.exit_code}: {result.error}"
    )
