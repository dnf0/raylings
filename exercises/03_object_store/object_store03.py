"""
Exercise: exercises/03_object_store/object_store03.py
Topic: Object Immutability & Safe Buffer Copies

Context & Why:
To ensure data consistency across concurrent readers without lock contention, objects stored in
Ray's Plasma store are strictly **immutable**. NumPy arrays retrieved from Plasma have their
`flags.writeable` set to `False`.

Attempting to mutate an in-place Plasma buffer directly (`arr[0] = 99`) raises a `ValueError`.
To modify data, workers must explicitly create a mutable copy via `arr.copy()`.

Instructions:
1. Retrieve an array from Plasma and observe that in-place mutation fails.
2. Create an explicit copy via `.copy()` before performing mutations.
"""

# I AM NOT DONE

import numpy as np
import ray


# TODO: Define normalize_array remote function
def normalize_array(arr: np.ndarray) -> np.ndarray:
    # Must make a copy to mutate safely!
    # arr_copy = arr.copy()
    # arr_copy[arr_copy < 0] = 0.0
    # return arr_copy
    pass


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

    # TODO: 2. Process data_ref through normalize_array.remote()
    # normalized_ref = normalize_array.remote(data_ref)
    # result = ray.get(normalized_ref)
    result = None

    expected = np.array([0.0, 10.0, 0.0, 8.0, 0.0, 3.0])
    assert result is not None, "result should not be None"
    assert np.array_equal(result, expected), f"Expected {expected}, got {result}"
    # Verify original in Plasma was NOT modified
    assert np.array_equal(ray.get(data_ref), data), "Original array in Plasma must remain immutable"
    print(
        f"✓ object_store03 verified: Plasma immutability and safe copy mutation validated ({result})!"
    )


if __name__ == "__main__":
    verify()
