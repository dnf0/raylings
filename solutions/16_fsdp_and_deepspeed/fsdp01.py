"""Chapter 16: DeepSpeed & PyTorch FSDP - Solution 1: PyTorch FSDP with Ray Train ScalingConfig.

Reference Solution for fsdp01.
"""

import functools
import os
from typing import Any

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
import ray.train
import ray.train.torch
import torch
import torch.nn as nn
import torch.optim as optim
from ray.train import ScalingConfig
from ray.train.torch import TorchTrainer
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import ShardingStrategy
from torch.distributed.fsdp.wrap import size_based_auto_wrap_policy


class ToyBlock(nn.Module):
    """Submodule block for FSDP auto-wrap policy demonstration."""

    def __init__(self, in_features: int, out_features: int) -> None:
        super().__init__()
        self.linear = nn.Linear(in_features, out_features)
        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.relu(self.linear(x))


class ToyNet(nn.Module):
    """Multi-layer network containing wrapped submodule blocks."""

    def __init__(
        self, in_features: int = 16, hidden_features: int = 32, out_features: int = 1
    ) -> None:
        super().__init__()
        self.block1 = ToyBlock(in_features, hidden_features)
        self.block2 = ToyBlock(hidden_features, hidden_features)
        self.head = nn.Linear(hidden_features, out_features)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.block1(x)
        x = self.block2(x)
        return self.head(x)


def wrap_fsdp_model(
    model: nn.Module,
    sharding_strategy: ShardingStrategy = ShardingStrategy.FULL_SHARD,
    min_num_params: int = 50,
) -> FSDP:
    """Wrap a PyTorch model in FullyShardedDataParallel with a size-based auto-wrap policy."""
    auto_wrap_policy = functools.partial(size_based_auto_wrap_policy, min_num_params=min_num_params)
    return FSDP(
        model,
        auto_wrap_policy=auto_wrap_policy,
        sharding_strategy=sharding_strategy,
        device_id=torch.device("cpu"),
    )


def train_loop(config: dict[str, Any]) -> dict[str, float]:
    """Train loop executed on each Ray Train distributed worker with FSDP."""
    epochs = config.get("epochs", 25)
    lr = config.get("lr", 0.05)
    strategy = config.get("sharding_strategy", ShardingStrategy.FULL_SHARD)

    torch.manual_seed(42 + ray.train.get_context().get_world_rank())

    model = ToyNet()
    fsdp_model = wrap_fsdp_model(model, sharding_strategy=strategy)
    optimizer = optim.Adam(fsdp_model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    # Deterministic synthetic regression data
    generator = torch.Generator().manual_seed(100)
    x = torch.randn(32, 16, generator=generator)
    true_w = torch.ones(16, 1)
    y = torch.matmul(x, true_w)

    initial_loss = 0.0
    final_loss = 0.0

    for epoch in range(epochs):
        optimizer.zero_grad()
        output = fsdp_model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()

        current_loss = float(loss.item())
        if epoch == 0:
            initial_loss = current_loss
        final_loss = current_loss

    report_dict = {"initial_loss": initial_loss, "final_loss": final_loss}
    ray.train.report(report_dict)
    return report_dict


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    scaling_config = ScalingConfig(num_workers=2, use_gpu=False)
    trainer = TorchTrainer(
        train_loop_per_worker=train_loop,
        train_loop_config={
            "epochs": 25,
            "lr": 0.05,
            "sharding_strategy": ShardingStrategy.FULL_SHARD,
        },
        scaling_config=scaling_config,
    )
    result = trainer.fit()

    assert result is not None, "TorchTrainer result must not be None"
    assert result.error is None, f"Training failed with error: {result.error}"

    metrics = result.return_value
    assert metrics is not None, "Expected return_value from training loop"
    assert "initial_loss" in metrics and "final_loss" in metrics, f"Missing loss metrics: {metrics}"

    initial_loss = metrics["initial_loss"]
    final_loss = metrics["final_loss"]
    assert final_loss < initial_loss, (
        f"Loss did not decrease: initial={initial_loss:.4f}, final={final_loss:.4f}"
    )
    assert final_loss < 0.5, f"Final loss too high: {final_loss:.4f}"

    print(
        f"✓ fsdp01 verified: 2-worker FSDP training converged (initial={initial_loss:.4f} -> final={final_loss:.4f})!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
