"""Chapter 3: Plasma Object Store & Zero-Copy - Solution 1: Zero-Copy Plasma Reads.

Reference Solution for object_store01.
"""

import numpy as np
import ray
from ray import ObjectRef


@ray.remote
def compute_stats(arr: np.ndarray) -> tuple[float, float]:
    return float(np.mean(arr)), float(np.std(arr))


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    data = np.arange(1000, dtype=np.float64)

    data_ref: ObjectRef = ray.put(data)
    retrieved_data: np.ndarray = ray.get(data_ref)

    stats_ref = compute_stats.remote(data_ref)
    mean_val, std_val = ray.get(stats_ref)

    assert data_ref is not None, "data_ref must be created with ray.put()"
    assert isinstance(retrieved_data, np.ndarray), "retrieved_data must be a NumPy array"
    assert (
        retrieved_data.flags.writeable is False
    ), "Plasma shared memory NumPy array should be read-only (flags.writeable == False)"
    assert np.isclose(mean_val, 499.5), f"Expected mean 499.5, got {mean_val}"
    assert std_val > 0.0, f"Expected non-zero std, got {std_val}"
    print(
        f"✓ object_store01 verified: Zero-copy Plasma array validated (mean={mean_val:.1f}, writeable={retrieved_data.flags.writeable})!"
    )


if __name__ == "__main__":
    verify()
