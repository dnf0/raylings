"""Chapter 8: Ray Data for High-Throughput ETL - Solution 3: Stateful Transforms with ActorPoolStrategy.

Reference Solution for data03.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import numpy as np
import ray
import ray.data


class ModelScorer:
    def __init__(self) -> None:
        self.bias = 100

    def __call__(self, batch: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        batch["score"] = batch["raw_val"] + self.bias
        return batch


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [{"raw_val": i} for i in range(20)]
    ds = ray.data.from_items(items)

    scored = ds.map_batches(
        ModelScorer,
        compute=ray.data.ActorPoolStrategy(min_size=1, max_size=2),
        batch_format="numpy",
    )
    total_rows = scored.count()
    first_row = scored.take(1)[0]

    assert total_rows == 20, f"Expected 20 rows, got {total_rows}"
    assert first_row.get("score") == 100, f"Expected first score 100, got {first_row}"
    print(
        f"✓ data03 verified: Stateful ActorPoolStrategy applied across {total_rows} rows (first={first_row})!"
    )


if __name__ == "__main__":
    verify()
