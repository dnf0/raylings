"""Chapter 10: Ray Train - Exercise 1: PyTorch TorchTrainer & ScalingConfig.

Ray Train provides distributed deep learning orchestration for PyTorch (DDP).

Your Task:
- In `train_loop(config)`:
  - Create model `nn.Linear(1, 1)` wrapped in `ray.train.torch.prepare_model(model)`.
  - Train with SGD for 20 steps on `x = torch.tensor([[1.0], [2.0]]), y = torch.tensor([[2.0], [4.0]])`.
  - Report and return `{"loss": final_loss}`.
- In `verify()`:
  - Run `TorchTrainer(train_loop, scaling_config=ScalingConfig(num_workers=2, use_gpu=False))`.
  - Assert that final loss is < 0.5.
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
