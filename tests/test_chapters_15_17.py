"""Test suite for Chapters 15 to 17 (Distributed LLM Serving, FSDP & DeepSpeed, Multimodal & Vectors).

Verifies:
1. Exercise skeletons exist, contain the '# I AM NOT DONE' marker, and fail initially.
2. Reference solutions exist, do not contain the marker, and pass cleanly.
"""

import pytest

from raylings.manifest import get_manifest
from raylings.models import Exercise
from raylings.runner import ExerciseRunner

pytestmark = pytest.mark.heavy


MANIFEST = get_manifest()

CHAPTER_15_17_EXERCISES = [
    ex
    for ex in MANIFEST.all_exercises
    if ex.chapter_name
    in [
        "15_vllm_and_llms",
        "16_fsdp_and_deepspeed",
        "17_multimodal_and_vectors",
    ]
]


def test_chapter_15_17_exercise_count() -> None:
    """Verify that Chapters 15 to 17 contain 12 exercises in total."""
    assert len(CHAPTER_15_17_EXERCISES) == 12, (
        f"Expected 12 exercises for Ch 15-17, found {len(CHAPTER_15_17_EXERCISES)}"
    )


@pytest.mark.parametrize("exercise", CHAPTER_15_17_EXERCISES, ids=lambda ex: ex.name)
def test_exercise_skeleton_fails_with_marker(exercise: Exercise) -> None:
    """Verify that every exercise skeleton exists, contains the marker, and fails."""
    runner = ExerciseRunner()
    ex_path = exercise.file_path
    assert ex_path.exists(), f"Exercise file missing: {ex_path}"

    has_marker = runner.check_marker(ex_path)
    assert has_marker is True, f"Exercise {ex_path} must contain '# I AM NOT DONE' marker"

    result = runner.run_exercise(exercise, timeout=30.0)
    assert result.passed is False, f"Exercise skeleton {exercise.name} should fail initially"


@pytest.mark.parametrize("exercise", CHAPTER_15_17_EXERCISES, ids=lambda ex: ex.name)
def test_solution_file_passes_cleanly(exercise: Exercise) -> None:
    """Verify that every reference solution exists, has no marker, and passes cleanly."""
    runner = ExerciseRunner()
    sol_path = exercise.solution_path
    assert sol_path.exists(), f"Solution file missing: {sol_path}"

    has_marker = runner.check_marker(sol_path)
    assert has_marker is False, f"Solution {sol_path} must NOT contain the marker"

    result = runner.run_solution(exercise, timeout=90.0)
    assert result.passed is True, (
        f"Solution {exercise.name} failed with exit_code={result.exit_code}: {result.error}"
    )
