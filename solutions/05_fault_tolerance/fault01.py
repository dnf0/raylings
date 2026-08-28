"""Chapter 5: Fault Tolerance & Recovery - Solution 1: Automatic Task Retries.

Reference Solution for fault01.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import tempfile
from pathlib import Path

import ray


@ray.remote(max_retries=3, retry_exceptions=True)
def unstable_task(attempt_file: str) -> str:
    path = Path(attempt_file)
    attempts = int(path.read_text(encoding="utf-8")) if path.exists() else 0
    path.write_text(str(attempts + 1), encoding="utf-8")
    if attempts < 2:
        raise RuntimeError("Transient glitch!")
    return "success_on_retry"


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        attempt_path = tmp.name
    Path(attempt_path).unlink()

    try:
        result = ray.get(unstable_task.remote(attempt_path))
        total_attempts = int(Path(attempt_path).read_text(encoding="utf-8"))

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
