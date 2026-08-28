"""
Exercise: exercises/03_object_store/object_store01.py
Topic: Zero-Copy Plasma Shared Memory Reads

Context & Why:
Ray features an in-memory shared-memory object store called **Plasma**.
When large NumPy arrays, PyArrow tables, or tensors are stored in Plasma, worker processes on the
same physical machine can read them via memory-mapped shared buffers with **zero memory copies**
and zero deserialization overhead.

This allows multiple worker tasks to read a 10GB dataset concurrently without consuming 10GB RAM per worker.

Instructions:
1. Allocate a NumPy array and store it in the Plasma object store via `ray.put(arr)`.
2. Pass the `ObjectRef` to a worker task and verify that the worker receives a read-only view of the data.
"""

# I AM NOT DONE

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
