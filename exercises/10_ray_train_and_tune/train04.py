"""Chapter 10: Ray Train - Exercise 4: Distributed Checkpointing & Fault Recovery.

Checkpointing allows training jobs to persist model weights periodically and recover
seamlessly from hardware crashes or Spot instance preemption.

Your Task:
- In `train_loop(config)`:
  - Train model for 5 steps.
  - In a `tempfile.TemporaryDirectory()`, save weights `torch.save(model.state_dict(), path)`.
  - Create `checkpoint = Checkpoint.from_directory(temp_dir)` and call `ray.train.report(..., checkpoint=checkpoint)`.
- In `verify()`:
  - Run `TorchTrainer`, verify `result.checkpoint` exists, restore and load weights.
"""

# I AM NOT DONE
import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import tempfile

import ray
import ray.train
import ray.train.torch
import torch
import torch.nn as nn
from ray.train import Checkpoint, ScalingConfig
from ray.train.torch import TorchTrainer


def train_loop(config: dict) -> None:
    # TODO: Implement checkpoint saving inside temporary directory and report checkpoint
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Run TorchTrainer and restore checkpoint
    result = None

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
