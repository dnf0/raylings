"""Chapter 1: Ray Core Foundations - Solution 5: Dynamic Completion with ray.wait().

Reference Solution for basics05.
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
    unready_refs: list[ObjectRef] = [
        variable_task.remote(task_id, duration) for task_id, duration in tasks_config
    ]

    finished_task_ids: list[int] = []

    while unready_refs:
        ready, unready_refs = ray.wait(unready_refs, num_returns=1)
        for ref in ready:
            task_id, _ = ray.get(ref)
            finished_task_ids.append(task_id)

    return finished_task_ids


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    tasks_config = [
        (1, 0.04),
        (2, 0.08),
        (3, 0.01),
    ]

    completed_order = process_as_completed(tasks_config)

    expected_order = [3, 1, 2]
    assert (
        completed_order == expected_order
    ), f"Expected completion order {expected_order}, but got {completed_order}"
    print(f"✓ basics05 verified: Dynamic ray.wait() streaming completed in order {completed_order}!")


if __name__ == "__main__":
    verify()
