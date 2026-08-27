"""Chapter 3: Plasma Object Store & Zero-Copy - Solution 3: Object Immutability & Read-Only Semantics.

Reference Solution for object_store03.
"""

import numpy as np
import ray


@ray.remote
def normalize_array(arr: np.ndarray) -> np.ndarray:
    arr_copy = arr.copy()
    arr_copy[arr_copy < 0] = 0.0
    return arr_copy


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    data = np.array([-5.0, 10.0, -2.0, 8.0, -1.0, 3.0])
    data_ref = ray.put(data)

    # 1. Verify read-only immutability
    plasma_arr = ray.get(data_ref)
    mutation_failed = False
    try:
        plasma_arr[0] = 999.0
    except ValueError:
        mutation_failed = True

    assert mutation_failed, "Direct mutation of Plasma zero-copy array should raise ValueError"

    normalized_ref = normalize_array.remote(data_ref)
    result = ray.get(normalized_ref)

    expected = np.array([0.0, 10.0, 0.0, 8.0, 0.0, 3.0])
    assert result is not None, "result should not be None"
    assert np.array_equal(result, expected), f"Expected {expected}, got {result}"
    assert np.array_equal(ray.get(data_ref), data), "Original array in Plasma must remain immutable"
    print(
        f"✓ object_store03 verified: Plasma immutability and safe copy mutation validated ({result})!"
    )


if __name__ == "__main__":
    verify()
