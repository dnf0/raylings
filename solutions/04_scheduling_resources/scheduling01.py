"""Chapter 4: Scheduling & Resources - Solution 1: Fractional & Custom Resources.

Reference Solution for scheduling01.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray


@ray.remote(num_cpus=0.25)
def light_task(val: int) -> int:
    return val * 2


@ray.remote(resources={"custom_accelerator": 1})
def accelerator_task(val: int) -> int:
    return val**2


def verify() -> None:
    ray.init(ignore_reinit_error=True, resources={"custom_accelerator": 4})

    light_refs = [light_task.remote(i) for i in [1, 2, 3, 4]]
    light_results = ray.get(light_refs)

    accel_refs = [accelerator_task.remote(i) for i in [10, 20]]
    accel_results = ray.get(accel_refs)

    assert light_results == [2, 4, 6, 8], f"Expected [2, 4, 6, 8], got {light_results}"
    assert accel_results == [100, 400], f"Expected [100, 400], got {accel_results}"
    print(
        f"✓ scheduling01 verified: Fractional & custom resources scheduled successfully ({light_results}, {accel_results})!"
    )


if __name__ == "__main__":
    verify()
