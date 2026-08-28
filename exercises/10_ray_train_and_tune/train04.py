"""
Exercise: exercises/10_ray_train_and_tune/train04.py
Topic: Fault-Tolerant Training & Elastic Worker Recovery

Context & Why:
When training deep neural networks for days on spot instances, worker preemption is inevitable.
Ray Train integrates with `RunConfig(failure_config=FailureConfig(max_failures=3))` to automatically
re-provision failed workers and resume training from the latest valid checkpoint.

Instructions:
1. Configure failure recovery in `RunConfig`.
2. Simulate worker failure and verify seamless training resumption.
"""

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
