"""
Exercise: exercises/01_basics/basics05.py
Topic: Dynamic Completion Processing with ray.wait()

Context & Why:
When running heterogeneous distributed tasks with varying runtimes, `ray.get(refs)` blocks until
the slowest task completes. If 99 tasks finish in 10ms and 1 task takes 10s, `ray.get(refs)` forces
the driver to sit idle for 10s before processing any finished data.

`ray.wait(object_refs, num_returns=1, timeout=None)` solves this by returning two lists:
`(ready_refs, unready_refs)` as soon as `num_returns` tasks are completed.
Using a `while unready_refs:` loop enables streaming pipeline architectures, where downstream
processing begins immediately as tasks finish.

Instructions:
1. Implement `process_as_completed(tasks_config)` using `ray.wait()` inside a `while unready_refs:` loop.
2. In each iteration, extract completed task IDs from `ready_refs` and update `unready_refs`.
3. Return task IDs in the order they finished.
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
