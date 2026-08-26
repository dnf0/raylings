"""Chapter 3: Plasma Object Store & Zero-Copy - Solution 2: ray.put() vs Implicit Serialization.

Reference Solution for object_store02.
"""

import numpy as np
import ray
from ray import ObjectRef


@ray.remote
def process_slice(matrix: np.ndarray, row_idx: int) -> float:
    return float(matrix[row_idx].sum())


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    matrix = np.arange(2500, dtype=np.float64).reshape((50, 50))
    target_rows = [0, 10, 20, 30]

    matrix_ref: ObjectRef = ray.put(matrix)
    refs = [process_slice.remote(matrix_ref, r) for r in target_rows]
    results: list[float] = ray.get(refs)

    expected = [float(matrix[r].sum()) for r in target_rows]
    assert matrix_ref is not None, "matrix_ref must be created with ray.put()"
    assert np.allclose(results, expected), f"Expected {expected}, got {results}"
    print(
        f"✓ object_store02 verified: ray.put() shared single copy across {len(target_rows)} worker tasks ({results})!"
    )


if __name__ == "__main__":
    verify()
