"""Chapter 10: Ray Train - Exercise 3: Multi-Worker Gradient Sync & Metrics.

In PyTorch DDP, worker processes maintain synchronized parameters via All-Reduce.

Your Task:
- In `train_loop(config)`:
  - Discover `world_size = ray.train.get_context().get_world_size()`.
  - Train model for 3 epochs.
  - Return `{"epoch": 2, "world_size": world_size}`.
- In `verify()`:
  - Run 2-worker TorchTrainer and verify world_size is 2 and epoch is 2.
"""

# I AM NOT DONE
import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
import ray.train
import ray.train.torch
import torch
import torch.nn as nn
import torch.optim as optim
from ray.train import ScalingConfig
from ray.train.torch import TorchTrainer


def train_loop(config: dict) -> dict:
    # TODO: Implement multi-epoch training and return dict
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Run TorchTrainer with 2 workers
    result = None

    assert result is not None, "Trainer result must not be None"

    assert result.error is None, f"Training failed: {result.error}"
    print("✓ train03 verified: Multi-worker gradient sync completed across workers!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
