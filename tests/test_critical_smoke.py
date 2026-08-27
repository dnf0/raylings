"""Critical curriculum smoke tests for CI.

Executes a small, representative subset of Ray Core exercises and solutions
to ensure end-to-end runtime execution works without launching dozens of clusters.
"""

from raylings.manifest import get_exercise_by_name
from raylings.runner import ExerciseRunner


def test_critical_smoke_representative_exercises():
    """Verify representative exercises fail with marker and solutions pass cleanly."""
    runner = ExerciseRunner()
    representative_names = ["basics01", "actors01", "object_store01"]

    for name in representative_names:
        ex = get_exercise_by_name(name)
        assert ex is not None, f"Exercise {name} not found in manifest"

        # 1. Exercise skeleton should fail initially due to incomplete implementation
        skel_result = runner.run_exercise(ex)
        assert skel_result.passed is False, f"Skeleton {name} should have failed initially"

        # 2. Reference solution should pass cleanly
        sol_result = runner.run_solution(ex)
        assert sol_result.passed is True, (
            f"Solution {name} failed with exit_code={sol_result.exit_code}:\n"
            f"{sol_result.error}\nOutput:\n{sol_result.output}"
        )
