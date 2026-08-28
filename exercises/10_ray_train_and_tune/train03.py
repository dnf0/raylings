"""
Exercise: exercises/10_ray_train_and_tune/train03.py
Topic: Distributed Metrics Reporting & Checkpoint Persistence

Context & Why:
`ray.train.report(metrics={"loss": loss}, checkpoint=checkpoint)` streams training loss/accuracy
to the driver and saves distributed model checkpoints to cloud or shared storage without blocking the training loop.

Instructions:
1. Call `ray.train.report` with epoch loss and PyTorch model state dictionary.
2. Verify checkpoints are persisted.
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
