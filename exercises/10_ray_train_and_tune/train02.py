# I AM NOT DONE
"""Chapter 10: Ray Train - Exercise 2: Distributed DataLoader via Data Sharding.

Ray Train automatically partitions datasets across distributed training workers.

Your Task:
- In `train_loop(config)`:
  - Retrieve the worker data shard via `shard = ray.train.get_dataset_shard("train")`.
  - Iterate over batches with `shard.iter_torch_batches(batch_size=5)`.
  - Count total samples processed on this worker and return `{"worker_samples": total_samples}`.
- In `verify()`:
  - Pass a 50-item dataset to `TorchTrainer` with 2 workers.
  - Assert that each worker processed exactly 25 samples.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
import ray.data
import ray.train
import ray.train.torch
from ray.train import ScalingConfig
from ray.train.torch import TorchTrainer


def train_loop(config: dict) -> dict:
    # TODO: Fetch shard and count samples
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [{"x": float(i), "y": float(2 * i)} for i in range(50)]
    dataset = ray.data.from_items(items)

    # TODO: Configure TorchTrainer with datasets={"train": dataset} and num_workers=2
    result = None

    assert result is not None, "Result must not be None"

    assert result.error is None, f"Training failed: {result.error}"
    print("✓ train02 verified: Distributed dataset sharded cleanly across workers!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
