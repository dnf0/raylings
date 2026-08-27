# I AM NOT DONE
"""Chapter 8: Ray Data for High-Throughput ETL - Exercise 3: Stateful Transforms with ActorPoolStrategy.

When applying heavy ML models (e.g. HuggingFace Transformers, PyTorch ResNets), loading
model weights in every task introduces severe overhead.
Ray Data allows you to define stateful transforms as callable Python classes and run them
across an elastic actor pool using `ActorPoolStrategy`.

Pattern:
```python
class MLPredictor:
    def __init__(self):
        # Initialized ONCE per worker actor
        self.model = load_my_model()

    def __call__(self, batch: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        batch["prediction"] = self.model.predict(batch["feature"])
        return batch

predictions = ds.map_batches(
    MLPredictor,
    compute=ray.data.ActorPoolStrategy(min_size=1, max_size=2),
    batch_format="numpy",
)
```

Your Task:
- Define a class `ModelScorer`:
  - `__init__(self)`: Initializes `self.bias = 100`.
  - `__call__(self, batch: dict[str, np.ndarray]) -> dict[str, np.ndarray]`:
    - Adds `batch["score"] = batch["raw_val"] + self.bias`.
    - Returns the updated batch.
- In `verify()`:
  - Create dataset from `[{'raw_val': i} for i in range(20)]`.
  - Apply `ds.map_batches(ModelScorer, compute=ray.data.ActorPoolStrategy(min_size=1, max_size=2), batch_format="numpy")`.
  - Check the output count and verify that the first item has `score == 100`.
"""

import numpy as np
import ray
import ray.data


# TODO: Define ModelScorer stateful class
class ModelScorer:
    def __init__(self) -> None:
        self.bias = 100

    def __call__(self, batch: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        # batch["score"] = batch["raw_val"] + self.bias
        # return batch
        return batch


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [{"raw_val": i} for i in range(20)]
    ds = ray.data.from_items(items)

    # TODO: Map batches using ModelScorer and ActorPoolStrategy
    # scored = ds.map_batches(
    #     ModelScorer,
    #     compute=ray.data.ActorPoolStrategy(min_size=1, max_size=2),
    #     batch_format="numpy",
    # )
    # total_rows = scored.count()
    # first_row = scored.take(1)[0]
    total_rows, first_row = None, {}

    assert total_rows == 20, f"Expected 20 rows, got {total_rows}"
    assert first_row.get("score") == 100, f"Expected first score 100, got {first_row}"
    print(
        f"✓ data03 verified: Stateful ActorPoolStrategy applied across {total_rows} rows (first={first_row})!"
    )


if __name__ == "__main__":
    verify()
