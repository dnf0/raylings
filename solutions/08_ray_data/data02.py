"""Chapter 8: Ray Data for High-Throughput ETL - Solution 2: Vectorized Batch Transforms (map_batches).

Reference Solution for data02.
"""

import numpy as np
import ray
import ray.data


def scale_and_filter_batch(batch: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    batch["scaled"] = batch["x"] * 10
    return batch


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [{"x": i} for i in range(50)]
    ds = ray.data.from_items(items)

    transformed = ds.map_batches(scale_and_filter_batch, batch_format="numpy")
    sample_rows = transformed.take(3)

    expected = [{"x": 0, "scaled": 0}, {"x": 1, "scaled": 10}, {"x": 2, "scaled": 20}]
    assert sample_rows == expected, f"Expected {expected}, got {sample_rows}"
    print(f"✓ data02 verified: Vectorized map_batches transformed rows cleanly ({sample_rows})!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
