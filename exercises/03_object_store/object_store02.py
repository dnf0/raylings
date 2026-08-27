"""Chapter 3: Plasma Object Store & Zero-Copy - Exercise 2: ray.put() vs Implicit Serialization.

When you pass a standard Python object (e.g., large array, dataset, model weights)
as an argument to multiple remote tasks:

    # ❌ ANTI-PATTERN (Repetitive Serialization):
    for _ in range(10):
        worker_task.remote(large_data)  # Serializes and copies `large_data` 10 times!

Each call implicitly copies and serializes `large_data` into the task specification,
wasting CPU cycles, memory, and IPC bandwidth.

    # ✓ PROPER PATTERN (Explicit ray.put):
    data_ref = ray.put(large_data)      # Stored ONCE in Plasma object store
    for _ in range(10):
        worker_task.remote(data_ref)    # Passes only a 28-byte pointer!

Key Rules:
1. If data size is > 100KB and passed to more than one task, ALWAYS use `ray.put()`.
2. Ray automatically de-references `data_ref` before passing the data to the task function.

Your Task:
- Define a remote task `@ray.remote def process_slice(matrix: np.ndarray, row_idx: int) -> float`
  that returns the sum of the specified row `float(matrix[row_idx].sum())`.
- Put a 50x50 matrix into the object store once with `ray.put()`.
- Launch 4 parallel tasks passing `matrix_ref` to calculate the row sum for rows 0, 10, 20, 30.
- Retrieve all results and verify against NumPy calculations.
"""

# I AM NOT DONE
import numpy as np
import ray
from ray import ObjectRef


# TODO: Define process_slice remote function
def process_slice(matrix: np.ndarray, row_idx: int) -> float:
    return float(matrix[row_idx].sum())


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # 50x50 test matrix
    matrix = np.arange(2500, dtype=np.float64).reshape((50, 50))
    target_rows = [0, 10, 20, 30]

    # TODO: 1. Put matrix into Plasma once using ray.put()
    # matrix_ref: ObjectRef = ray.put(matrix)
    matrix_ref: ObjectRef = None  # type: ignore

    # TODO: 2. Launch 4 process_slice.remote(matrix_ref, r) tasks
    # refs = [process_slice.remote(matrix_ref, r) for r in target_rows]
    # results = ray.get(refs)
    results: list[float] = []

    expected = [float(matrix[r].sum()) for r in target_rows]
    assert matrix_ref is not None, "matrix_ref must be created with ray.put()"
    assert np.allclose(results, expected), f"Expected {expected}, got {results}"
    print(
        f"✓ object_store02 verified: ray.put() shared single copy across {len(target_rows)} worker tasks ({results})!"
    )


if __name__ == "__main__":
    verify()
