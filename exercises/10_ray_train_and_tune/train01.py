"""
Exercise: exercises/10_ray_train_and_tune/train01.py
Topic: TorchTrainer & ScalingConfig Distributed PyTorch

Context & Why:
`ray.train.torch.TorchTrainer` provides native orchestration for PyTorch Distributed Data Parallel (DDP).
`ScalingConfig(num_workers=2, use_gpu=False)` coordinates worker processes, sets up `torch.distributed`
process groups (NCCL/Gloo), and handles rank assignments automatically.

Instructions:
1. Define a distributed training function.
2. Instantiate `TorchTrainer` with `ScalingConfig(num_workers=2)` and execute `trainer.fit()`.
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
    # TODO: Implement train_loop with prepare_model, SGD training, and return loss
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Configure 2-worker TorchTrainer and verify result
    # scaling_config = ScalingConfig(num_workers=2, use_gpu=False)
    # trainer = TorchTrainer(train_loop_per_worker=train_loop, scaling_config=scaling_config)
    # result = trainer.fit()
    result = None

    assert result is not None, "Trainer result must not be None"

    assert result.error is None, f"Training failed: {result.error}"
    print("✓ train01 verified: 2-worker TorchTrainer trained successfully!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
