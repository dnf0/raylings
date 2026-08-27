"""Chapter 10: Ray Train - Solution 4: Distributed Checkpointing & Fault Recovery.

Reference Solution for train04.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import tempfile
import ray
import ray.train
import ray.train.torch
import torch
import torch.nn as nn
import torch.optim as optim
from ray.train import Checkpoint, ScalingConfig
from ray.train.torch import TorchTrainer


def train_loop(config: dict) -> None:
    model = nn.Linear(1, 1)
    model = ray.train.torch.prepare_model(model)
    optimizer = optim.SGD(model.parameters(), lr=0.1)

    x = torch.tensor([[1.0], [2.0]])
    y = torch.tensor([[2.0], [4.0]])

    for _ in range(5):
        optimizer.zero_grad()
        loss = nn.MSELoss()(model(x), y)
        loss.backward()
        optimizer.step()

    with tempfile.TemporaryDirectory() as temp_dir:
        unwrapped = getattr(model, "module", model)
        torch.save(unwrapped.state_dict(), os.path.join(temp_dir, "model.pt"))
        checkpoint = Checkpoint.from_directory(temp_dir)
        ray.train.report({"loss": float(loss.item())}, checkpoint=checkpoint)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    scaling_config = ScalingConfig(num_workers=1, use_gpu=False)
    trainer = TorchTrainer(train_loop_per_worker=train_loop, scaling_config=scaling_config)
    result = trainer.fit()

    assert result is not None, "Trainer result must not be None"
    assert result.checkpoint is not None, "Expected a checkpoint in result"

    with tempfile.TemporaryDirectory() as restore_dir:
        result.checkpoint.to_directory(restore_dir)
        checkpoint_path = os.path.join(restore_dir, "model.pt")
        assert os.path.exists(checkpoint_path), f"Missing checkpoint file: {checkpoint_path}"
        state_dict = torch.load(checkpoint_path, weights_only=True)
        assert "weight" in state_dict, f"Expected 'weight' key in state_dict: {state_dict.keys()}"

    print("✓ train04 verified: Distributed checkpoint created, reported, and restored cleanly!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
