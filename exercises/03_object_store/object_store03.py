"""Chapter 3: Plasma Object Store & Zero-Copy - Exercise 3: Object Immutability & Read-Only Semantics.

Objects residing in Ray's Plasma object store are strictly IMMUTABLE.

Why?
If multiple worker processes or threads share the exact same physical memory buffer
via zero-copy, allowing one worker to mutate that memory in-place would silently corrupt
the data for all other workers reading it.

Behavior:
1. In-place Mutation Fails: Trying to write to a zero-copy array (`arr[0] = 99`) raises:
   `ValueError: assignment destination is read-only`.
2. Safe Mutation via `.copy()`: If a task needs to modify an array in-place (e.g. applying
   transformations or data normalization), it must make an explicit mutable copy:
   `mutable_arr = arr.copy()`.

Your Task:
- Define a remote function `normalize_array(arr: np.ndarray) -> np.ndarray` that:
  - Demonstrates safe mutation by creating a copy: `arr_copy = arr.copy()`
  - Replaces all negative values in `arr_copy` with `0.0`
  - Returns `arr_copy`
- Store a numpy array with negative values in Plasma with `ray.put()`.
- Test that directly mutating the array retrieved from Plasma raises `ValueError`.
- Process the array through `normalize_array.remote()` and verify the returned result.
"""

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
