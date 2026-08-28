"""
Exercise: exercises/10_ray_train_and_tune/train02.py
Topic: Distributed Dataset Sharding in Ray Train

Context & Why:
In DDP training, each worker rank must only process its assigned shard of data to prevent redundant gradient computations.
`ray.train.torch.prepare_data_loader(loader)` or `ray.train.get_dataset_shard("train")` automatically
partitions data across ranks with zero manual math.

Instructions:
1. Shard dataset across training workers using Ray Train data APIs.
2. Verify each worker receives unique data partitions.
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
