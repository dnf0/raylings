"""Chapter 1: Ray Core Foundations - Solution 3: Parallel Pipeline Execution.

Reference Solution for basics03.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import time

import ray


@ray.remote
def simulate_work(duration: float, task_id: int) -> int:
    time.sleep(duration)
    return task_id * 2


def run_sequential(durations: list[float]) -> tuple[list[int], float]:
    """Runs tasks sequentially by calling ray.get() inside the loop."""
    start = time.perf_counter()
    results = []
    for i, d in enumerate(durations):
        ref = simulate_work.remote(d, i)
        results.append(ray.get(ref))
    elapsed = time.perf_counter() - start
    return results, elapsed


def run_parallel(durations: list[float]) -> tuple[list[int], float]:
    """Runs all tasks concurrently in parallel."""
    start = time.perf_counter()
    refs = [simulate_work.remote(d, i) for i, d in enumerate(durations)]
    results = ray.get(refs)
    elapsed = time.perf_counter() - start
    return results, elapsed


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    durations = [0.08, 0.08, 0.08, 0.08]

    seq_results, seq_time = run_sequential(durations)
    par_results, par_time = run_parallel(durations)

    expected = [0, 2, 4, 6]
    assert seq_results == expected
    assert par_results == expected, f"Expected {expected}, got {par_results}"

    print(f"Sequential time: {seq_time:.3f}s | Parallel time: {par_time:.3f}s")
    assert par_time < seq_time * 0.75, (
        f"Parallel execution ({par_time:.3f}s) was not significantly faster than sequential ({seq_time:.3f}s)"
    )
    print("✓ basics03 verified: Parallel task execution pipeline confirmed!")


if __name__ == "__main__":
    verify()
