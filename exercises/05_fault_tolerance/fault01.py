# I AM NOT DONE
"""Chapter 5: Fault Tolerance & Recovery - Exercise 1: Automatic Task Retries.

In distributed computing, transient failures (network blips, memory spikes, spot interruptions)
are inevitable. Ray provides automatic retry mechanisms for tasks:

- `max_retries`: Number of times Ray will re-execute a task if the worker process crashes
  or (when `retry_exceptions=True`) if an exception is raised.
  Default is 3. Set to `-1` for infinite retries or `0` to disable.
- `retry_exceptions`: If `True`, user-level application exceptions will trigger retries.
  You can also pass a list of specific exception types, e.g. `retry_exceptions=[ConnectionError, TimeoutError]`.

Example:
    @ray.remote(max_retries=3, retry_exceptions=True)
    def flaky_network_call(attempt_file: str):
        ...

Your Task:
- Define a `@ray.remote(max_retries=3, retry_exceptions=True)` function `unstable_task(attempt_file: str) -> str`:
  - Reads the current attempt count from `attempt_file` (0 if file does not exist).
  - Writes `attempts + 1` to `attempt_file`.
  - If `attempts < 2`, raises `RuntimeError("Transient glitch!")`.
  - Otherwise, returns `"success_on_retry"`.
- In `verify()`, run `unstable_task` and assert that it successfully resolves to `"success_on_retry"`
  after 2 retries (total 3 attempts).
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
