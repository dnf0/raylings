# I AM NOT DONE
"""Chapter 4: Scheduling & Resources - Exercise 1: Fractional & Custom Resources.

In Ray, tasks and actors are scheduled dynamically based on resource declarations.
Ray does NOT enforce physical OS isolation (cgroups) for CPUs; rather, resource declarations
act as logical scheduling tokens.

Key Resource Features:
1. Fractional CPUs: You can request `< 1.0` CPU (e.g. `num_cpus=0.25`), allowing multiple
   lightweight I/O tasks or actors to share a single CPU core.
2. Custom Resources: You can define arbitrary cluster resource tags (e.g. `resources={"custom_accelerator": 1}`,
   `"A100": 2`, `"fpga": 1`) when starting nodes or `ray.init(resources={...})`. Tasks requesting
   those resources will only be scheduled on nodes possessing available tokens.

Example:
    @ray.remote(num_cpus=0.5)
    def io_bound_task(url: str):
        ...

    @ray.remote(resources={"custom_accelerator": 1})
    def accelerator_task(matrix):
        ...

Your Task:
- Define a `@ray.remote` function `light_task(val: int) -> int` that requests `0.25` CPU and returns `val * 2`.
- Define a `@ray.remote` function `accelerator_task(val: int) -> int` that requests 1 unit of `"custom_accelerator"`
  and returns `val ** 2`.
- In `verify()`, launch 4 `light_task`s concurrently and 2 `accelerator_task`s concurrently.
- Collect the results and verify their correctness.
"""

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
