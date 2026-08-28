"""
Exercise: exercises/03_object_store/object_store02.py
Topic: ray.put() vs Implicit Parameter Serialization

Context & Why:
When you pass a large Python object (e.g. 50MB array) as a raw argument to 100 remote tasks,
Ray implicitly serializes and copies that 50MB object 100 separate times!

Calling `ref = ray.put(large_data)` once, and then passing `ref` to the 100 tasks, stores the object
in Plasma **exactly once**. All 100 tasks receive lightweight references, reducing network/memory overhead from 5GB to 50MB.

Instructions:
1. Use `ray.put(large_matrix)` to pre-allocate shared memory before launching multiple worker tasks.
2. Pass the resulting `ObjectRef` to all tasks.
"""

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
