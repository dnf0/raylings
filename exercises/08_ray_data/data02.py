"""Chapter 8: Ray Data for High-Throughput ETL - Exercise 2: Vectorized Batch Transforms (map_batches).

While `ds.map(fn)` executes a Python function row-by-row, `ds.map_batches(fn, batch_format='numpy')`
processes entire tabular blocks using SIMD vectorized operations in NumPy or PyArrow.
This achieves 10x-50x higher throughput by eliminating Python per-row overhead.

Batch Function Signature:
When `batch_format="numpy"`, the transform function receives a `dict[str, np.ndarray]`
and returns a `dict[str, np.ndarray]`.

```python
import numpy as np

def normalize_batch(batch: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    batch["normalized"] = batch["val"] / 100.0
    return batch

transformed_ds = ds.map_batches(normalize_batch, batch_format="numpy")
```

Your Task:
- Define a batch transformation function `scale_and_filter_batch(batch: dict) -> dict`:
  - Adds a new column `batch["scaled"] = batch["x"] * 10`.
  - Returns the updated batch dict.
- In `verify()`:
  - Create a dataset from `[{'x': i} for i in range(50)]`.
  - Apply `ds.map_batches(scale_and_filter_batch, batch_format="numpy")`.
  - Take the first 3 rows using `transformed.take(3)`.
  - Verify that the first 3 rows contain `[{'x': 0, 'scaled': 0}, {'x': 1, 'scaled': 10}, {'x': 2, 'scaled': 20}]`.
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
    # transformed = ds.map_batches(scale_and_filter_batch, batch_format="numpy")
    # sample_rows = transformed.take(3)
    sample_rows = []

    expected = [{"x": 0, "scaled": 0}, {"x": 1, "scaled": 10}, {"x": 2, "scaled": 20}]
    assert sample_rows == expected, f"Expected {expected}, got {sample_rows}"
    print(f"✓ data02 verified: Vectorized map_batches transformed rows cleanly ({sample_rows})!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
