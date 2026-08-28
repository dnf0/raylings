"""
Exercise: exercises/04_scheduling_resources/scheduling01.py
Topic: Fractional CPUs and Custom Hardware Resources

Context & Why:
Ray's scheduler treats physical resources as logical quotas. You can specify fractional CPU requirements
(`num_cpus=0.25`), allowing 4 tasks to share a single CPU core, or request custom named resources
(e.g., `resources={"accelerator": 1}`).

This enables fine-grained multi-tenancy, co-locating light I/O workers on shared cores while reserving
dedicated hardware for heavy compute tasks.

Instructions:
1. Configure a task with fractional CPU requirements (`num_cpus=0.5`).
2. Launch multiple concurrent tasks and verify that Ray schedules them efficiently.
"""

# I AM NOT DONE

import ray


# TODO: Define light_task requesting 0.25 CPU
def light_task(val: int) -> int:
    return val * 2


# TODO: Define accelerator_task requesting 1 "custom_accelerator" resource
def accelerator_task(val: int) -> int:
    return val**2


def verify() -> None:
    # Initialize Ray with custom resources available in the cluster
    ray.init(ignore_reinit_error=True, resources={"custom_accelerator": 4})

    # TODO: Launch 4 light_tasks in parallel with inputs [1, 2, 3, 4]
    # light_refs = [light_task.remote(i) for i in [1, 2, 3, 4]]
    # light_results = ray.get(light_refs)
    light_results = None

    # TODO: Launch 2 accelerator_tasks in parallel with inputs [10, 20]
    # accel_refs = [accelerator_task.remote(i) for i in [10, 20]]
    # accel_results = ray.get(accel_refs)
    accel_results = None

    assert light_results == [2, 4, 6, 8], f"Expected [2, 4, 6, 8], got {light_results}"
    assert accel_results == [100, 400], f"Expected [100, 400], got {accel_results}"
    print(
        f"✓ scheduling01 verified: Fractional & custom resources scheduled successfully ({light_results}, {accel_results})!"
    )


if __name__ == "__main__":
    verify()
