# I AM NOT DONE
"""Chapter 1: Ray Core Foundations - Exercise 5: Dynamic Completion with ray.wait().

When running multiple tasks with varying execution times, `ray.get(refs)` blocks until
EVERY task has completed. If 9 tasks take 0.01s and 1 task takes 10s, `ray.get()` makes
you wait 10s before you can inspect ANY of the 9 finished tasks.

`ray.wait()` solves this by returning as soon as a specified number of tasks finish:

    ready_refs, unready_refs = ray.wait(
        object_refs,
        num_returns=1,      # Number of completed refs to wait for (default: 1)
        timeout=None,       # Maximum time to block (default: None = wait indefinitely)
    )

Key Concepts:
1. `ray.wait()` does not return Python values—it returns lists of `ObjectRef`s: `(ready_refs, unready_refs)`.
2. You can use a `while unready_refs:` loop to stream and process results in real-time as tasks finish.

Your Task:
- Implement `process_as_completed(durations)` using a `while unready_refs:` loop with `ray.wait()`.
- Collect the results in the order that tasks actually finish.
- Fast tasks should appear in the results list before slower tasks!
"""

import time

import ray
from ray import ObjectRef


@ray.remote
def variable_task(task_id: int, duration: float) -> tuple[int, float]:
    time.sleep(duration)
    return task_id, duration


def process_as_completed(tasks_config: list[tuple[int, float]]) -> list[int]:
    """Launch tasks and process their results as soon as each finishes."""
    # Launch all tasks
    unready_refs: list[ObjectRef] = [
        variable_task.remote(task_id, duration) for task_id, duration in tasks_config
    ]
    _ = unready_refs

    finished_task_ids: list[int] = []

    # TODO: Use a while loop with ray.wait() to consume unready_refs as they finish
    # while unready_refs:
    #     ready, unready_refs = ray.wait(unready_refs, num_returns=1)
    #     for ref in ready:
    #         task_id, _ = ray.get(ref)
    #         finished_task_ids.append(task_id)

    return finished_task_ids


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # Warm up Ray worker processes to eliminate cold start scheduling latency
    ray.get([variable_task.remote(0, 0.0) for _ in range(4)])

    # (task_id, sleep_duration)
    # Task 3 should finish first (0.01s), then Task 1 (0.12s), then Task 2 (0.30s)
    tasks_config = [
        (1, 0.12),
        (2, 0.30),
        (3, 0.01),
    ]

    completed_order = process_as_completed(tasks_config)

    expected_order = [3, 1, 2]
    assert completed_order == expected_order, (
        f"Expected completion order {expected_order}, but got {completed_order}"
    )
    print(
        f"✓ basics05 verified: Dynamic ray.wait() streaming completed in order {completed_order}!"
    )


if __name__ == "__main__":
    verify()
