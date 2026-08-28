"""
Exercise: exercises/01_basics/basics03.py
Topic: Parallel Pipeline Execution

Context & Why:
A classic distributed computing anti-pattern is calling `ray.get()` inside a task submission loop:
```python
# ❌ Anti-pattern (Sequential Stall):
for x in data:
    ref = task.remote(x)
    results.append(ray.get(ref))  # Blocks immediately! Destroys concurrency!
```
Calling `ray.get()` synchronously pauses the Python driver process until that specific worker finishes.
To achieve true parallelism across all available CPU cores, you must submit all tasks first to populate
the scheduler's queue, and then wait on the batch of ObjectRefs.

Instructions:
1. Fix `run_parallel()` so that all tasks are dispatched concurrently before calling `ray.get()`.
2. Confirm that parallel execution completes significantly faster than sequential execution.
"""

# I AM NOT DONE

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
        results.append(ray.get(ref))  # Serialized!
    elapsed = time.perf_counter() - start
    return results, elapsed


def run_parallel(durations: list[float]) -> tuple[list[int], float]:
    """TODO: Fix this function to run all tasks concurrently in parallel."""
    start = time.perf_counter()

    # TODO: 1. Launch all simulate_work.remote(d, i) tasks into a list of ObjectRefs
    # TODO: 2. Call ray.get() on the list of ObjectRefs once
    results: list[int] = []

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

    # Parallel time should be significantly faster than sequential time
    # Sequential ~ 0.32s; Parallel ~ 0.08s - 0.18s
    print(f"Sequential time: {seq_time:.3f}s | Parallel time: {par_time:.3f}s")
    assert par_time < seq_time * 0.75, (
        f"Parallel execution ({par_time:.3f}s) was not significantly faster than sequential ({seq_time:.3f}s)"
    )
    print("✓ basics03 verified: Parallel task execution pipeline confirmed!")


if __name__ == "__main__":
    verify()
