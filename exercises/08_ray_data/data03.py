"""
Exercise: exercises/08_ray_data/data03.py
Topic: Stateful Batch Inference with ActorPoolStrategy

Context & Why:
When performing batch inference with neural networks or heavy ML models, re-initializing the model
inside every task is prohibitively slow.

Passing `compute=ray.data.ActorPoolStrategy(min_size=N, max_size=M)` to `map_batches()` creates
a persistent pool of actor workers that keep model weights pinned in GPU/CPU memory across stream batches.

Instructions:
1. Define an inference class with a `__call__` method.
2. Execute `map_batches(InferenceClass, compute=ActorPoolStrategy(min_size=2))`.
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
