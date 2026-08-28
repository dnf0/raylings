"""
Exercise: exercises/08_ray_data/data02.py
Topic: Vectorized Batch Transformations with map_batches

Context & Why:
Processing items row-by-row in Python (`map()`) incurs heavy per-row interpretation overhead.
`map_batches(fn, batch_format="pyarrow" | "numpy" | "pandas")` passes zero-copy columnar chunks
to your transformation function, allowing vectorized SIMD execution via NumPy and PyArrow C-libraries.

Instructions:
1. Apply `map_batches` with vectorized NumPy / PyArrow transformations.
2. Verify throughput improvements over row-wise operations.
"""

# I AM NOT DONE

import numpy as np
import ray
import ray.data


# TODO: Define scale_and_filter_batch for NumPy batch format
def scale_and_filter_batch(batch: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    # batch["scaled"] = batch["x"] * 10
    # return batch
    return batch


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [{"x": i} for i in range(50)]
    ds = ray.data.from_items(items)

    # TODO: Apply map_batches
    # WHY: map_batches operates on zero-copy columnar Arrow batches to achieve maximum throughput.
    # transformed = ds.map_batches(scale_and_filter_batch, batch_format="numpy")
    # sample_rows = transformed.take(3)
    sample_rows = []

    expected = [{"x": 0, "scaled": 0}, {"x": 1, "scaled": 10}, {"x": 2, "scaled": 20}]
    assert sample_rows == expected, f"Expected {expected}, got {sample_rows}"
    print(f"✓ data02 verified: Vectorized map_batches transformed rows cleanly ({sample_rows})!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
