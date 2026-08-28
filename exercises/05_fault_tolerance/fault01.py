"""
Exercise: exercises/05_fault_tolerance/fault01.py
Topic: Automatic Task Retries & Idempotency

Context & Why:
Transient hardware glitches, spot instance interruptions, or network drops can cause remote tasks to fail.
Ray provides built-in task retries:
`@ray.remote(max_retries=3, retry_exceptions=True)` instructs Ray to automatically resubmit failed tasks.

Tasks must be **idempotent** (producing the same result when executed multiple times without side-effects).

Instructions:
1. Configure `max_retries=3` on an unreliable task.
2. Verify that transient worker exceptions are caught and retried until successful.
"""

import tempfile
from pathlib import Path

import ray


# TODO: Define unstable_task with max_retries=3 and retry_exceptions=True
def unstable_task(attempt_file: str) -> str:
    # path = Path(attempt_file)
    # attempts = int(path.read_text(encoding="utf-8")) if path.exists() else 0
    # path.write_text(str(attempts + 1), encoding="utf-8")
    # if attempts < 2:
    #     raise RuntimeError("Transient glitch!")
    # return "success_on_retry"
    return ""


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        attempt_path = tmp.name
    Path(attempt_path).unlink()  # Ensure file starts clean

    try:
        # TODO: Execute unstable_task
        # result = ray.get(unstable_task.remote(attempt_path))
        # total_attempts = int(Path(attempt_path).read_text(encoding="utf-8"))
        result, total_attempts = None, None

        assert result == "success_on_retry", f"Expected 'success_on_retry', got {result}"
        assert total_attempts == 3, (
            f"Expected 3 total attempts (2 failures + 1 success), got {total_attempts}"
        )
        print(
            f"✓ fault01 verified: Automatic task retry completed after {total_attempts} attempts!"
        )
    finally:
        if Path(attempt_path).exists():
            Path(attempt_path).unlink()


if __name__ == "__main__":
    verify()
