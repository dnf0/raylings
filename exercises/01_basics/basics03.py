"""Chapter 1: Ray Core Foundations - Exercise 3: Parallel Pipeline Execution.

A very common mistake when learning Ray is calling `ray.get()` immediately after
launching each remote task inside a loop:

    # ❌ ANTI-PATTERN (Sequential Execution):
    results = []
    for x in data:
        ref = slow_task.remote(x)
        results.append(ray.get(ref))  # Blocks immediately! No parallelism!

Calling `ray.get()` blocks the driver until that single task finishes, forcing tasks
to run sequentially one after another.

    # ✓ PROPER PATTERN (Parallel Execution):
    refs = [slow_task.remote(x) for x in data]  # Launch all tasks concurrently
    results = ray.get(refs)                     # Wait for all tasks in parallel

Key Concepts:
1. Ray tasks run asynchronously in background workers as soon as `.remote()` is called.
2. Collecting `ObjectRef`s allows the Ray scheduler to distribute work concurrently
   across available CPU cores.

Your Task:
- Refactor the sequential loop in `run_parallel()` to launch all 4 tasks concurrently.
- Fetch all results with a single `ray.get(refs)` call.
- The total parallel execution time must be significantly less than sequential time!
"""

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
