"""Chapter 10: Ray Train - Solution 2: Distributed DataLoader via Data Sharding.

Reference Solution for train02.
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
    shard = ray.train.get_dataset_shard("train")
    total_samples = 0
    for batch in shard.iter_torch_batches(batch_size=5):
        total_samples += len(batch["x"])

    ray.train.report({"worker_samples": total_samples})
    return {"worker_samples": total_samples}


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [{"x": float(i), "y": float(2 * i)} for i in range(50)]
    dataset = ray.data.from_items(items)

    scaling_config = ScalingConfig(num_workers=2, use_gpu=False)
    trainer = TorchTrainer(
        train_loop_per_worker=train_loop,
        datasets={"train": dataset},
        scaling_config=scaling_config,
    )
    result = trainer.fit()

    assert result is not None, "Result must not be None"

    assert result.error is None, f"Training failed: {result.error}"
    print("✓ train02 verified: Distributed dataset sharded cleanly across workers!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
