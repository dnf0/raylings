"""Chapter 10: Ray Train - Solution 1: PyTorch TorchTrainer & ScalingConfig.

Reference Solution for train01.
"""

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
    model = nn.Linear(1, 1)
    model = ray.train.torch.prepare_model(model)
    optimizer = optim.SGD(model.parameters(), lr=0.1)
    criterion = nn.MSELoss()

    x = torch.tensor([[1.0], [2.0]])
    y = torch.tensor([[2.0], [4.0]])

    final_loss = 0.0
    for _ in range(25):
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
        final_loss = float(loss.item())

    ray.train.report({"loss": final_loss})
    return {"loss": final_loss}


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    scaling_config = ScalingConfig(num_workers=2, use_gpu=False)
    trainer = TorchTrainer(train_loop_per_worker=train_loop, scaling_config=scaling_config)
    result = trainer.fit()

    assert result is not None, "Trainer result must not be None"

    assert result.error is None, f"Training failed: {result.error}"
    print("✓ train01 verified: 2-worker TorchTrainer trained successfully!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
