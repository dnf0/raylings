"""Test suite for Chapters 15 to 18 (Distributed LLM Serving, FSDP & DeepSpeed, Multimodal & Vectors, Quant Finance).

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

CHAPTER_15_17_EXERCISES = [
    ex
    for ex in MANIFEST.all_exercises
    if ex.chapter_name
    in [
        "15_vllm_and_llms",
        "16_fsdp_and_deepspeed",
        "17_multimodal_and_vectors",
        "18_quant_finance",
    ]
]


def test_chapter_15_18_exercise_count() -> None:
    """Verify that Chapters 15 to 18 contain 15 exercises in total."""
    assert len(CHAPTER_15_17_EXERCISES) == 15, (
        f"Expected 15 exercises for Ch 15-18, found {len(CHAPTER_15_17_EXERCISES)}"
    )


@pytest.mark.parametrize("exercise", CHAPTER_15_17_EXERCISES, ids=lambda ex: ex.name)
def test_exercise_skeleton_fails_initially(exercise: Exercise) -> None:
    """Verify that every exercise skeleton exists and fails initially."""
    runner = ExerciseRunner()
    ex_path = exercise.file_path
    assert ex_path.exists(), f"Exercise file missing: {ex_path}"

    result = runner.run_exercise(exercise, timeout=30.0)
    assert result.passed is False, f"Exercise skeleton {exercise.name} should fail initially"


@pytest.mark.parametrize("exercise", CHAPTER_15_17_EXERCISES, ids=lambda ex: ex.name)
def test_solution_file_passes_cleanly(exercise: Exercise) -> None:
    """Verify that every reference solution exists and passes cleanly."""
    runner = ExerciseRunner()
    sol_path = exercise.solution_path
    assert sol_path.exists(), f"Solution file missing: {sol_path}"

    result = runner.run_solution(exercise, timeout=90.0)
    assert result.passed is True, (
        f"Solution {exercise.name} failed with exit_code={result.exit_code}: {result.error}"
    )
