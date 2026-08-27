"""Chapter 3: Plasma Object Store & Zero-Copy - Exercise 1: Zero-Copy Plasma Reads.

Ray features an in-memory distributed object store called Plasma (allocated in shared memory,
such as `/dev/shm` on Linux or POSIX shared memory on macOS).

Zero-Copy Reads:
When large numerical datasets (such as NumPy arrays or PyArrow tables) are stored in Plasma
via `ray.put()`, worker processes on the same node do NOT need to deserialize or duplicate
the memory. Instead, Ray maps the shared memory buffer directly into each worker's address space.

Key Properties:
1. Shared Memory: Multiple worker tasks on the same machine read the same physical RAM.
2. Read-Only Protection: To prevent one worker from corrupting shared memory for other workers,
   NumPy arrays deserialized via zero-copy have `flags.writeable = False`.
3. Massive Throughput: Enables gigabytes of data to be read across workers with 0ms copy overhead.

Your Task:
- Define a remote task `@ray.remote def compute_stats(arr: np.ndarray) -> tuple[float, float]`
  that returns `(float(np.mean(arr)), float(np.std(arr)))`.
- Put a NumPy array of 1,000 numbers into Plasma with `ray.put()`.
- Retrieve the array locally with `ray.get()` and verify that `arr.flags.writeable` is `False`.
- Pass the `ObjectRef` to `compute_stats.remote()` and verify stats.
"""

import numpy as np
import ray
from ray import ObjectRef


# TODO: Define compute_stats remote function
def compute_stats(arr: np.ndarray) -> tuple[float, float]:
    return float(np.mean(arr)), float(np.std(arr))


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    data = np.arange(1000, dtype=np.float64)
    _ = data

    # TODO: 1. Store data into Plasma using ray.put()
    # data_ref: ObjectRef = ray.put(data)
    data_ref: ObjectRef = None  # type: ignore

    # TODO: 2. Retrieve data using ray.get()
    # retrieved_data: np.ndarray = ray.get(data_ref)
    retrieved_data: np.ndarray = None  # type: ignore

    # TODO: 3. Pass data_ref to compute_stats.remote() and get results
    # stats_ref = compute_stats.remote(data_ref)
    # mean_val, std_val = ray.get(stats_ref)
    mean_val, std_val = 0.0, 0.0

    assert data_ref is not None, "data_ref must be created with ray.put()"
    assert isinstance(retrieved_data, np.ndarray), "retrieved_data must be a NumPy array"
    assert retrieved_data.flags.writeable is False, (
        "Plasma shared memory NumPy array should be read-only (flags.writeable == False)"
    )
    assert np.isclose(mean_val, 499.5), f"Expected mean 499.5, got {mean_val}"
    assert std_val > 0.0, f"Expected non-zero std, got {std_val}"
    print(
        f"✓ object_store01 verified: Zero-copy Plasma array validated (mean={mean_val:.1f}, writeable={retrieved_data.flags.writeable})!"
    )


if __name__ == "__main__":
    verify()
