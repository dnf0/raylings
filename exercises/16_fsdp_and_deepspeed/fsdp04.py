"""Chapter 16: DeepSpeed & PyTorch FSDP - Exercise 4: Elastic Fault-Tolerant Distributed Checkpoints.

In large-scale distributed training, gathering all model and optimizer parameters onto rank 0 for monolithic
checkpoint saving introduces severe network bottlenecks and out-of-memory crashes. Sharded distributed
checkpointing enables each worker to persist its local parameter and optimizer partition independently.

Key Concepts:
- `Sharded State Saving`: Each rank saves only its local parameter slice (`rank_{i}_model.pt`) and optimizer
  partition (`rank_{i}_optim.pt`), avoiding single-node aggregation.
- `Atomic Metadata`: A centralized coordinator (rank 0) writes a lightweight atomic metadata descriptor
  (`metadata.json`) referencing step index, world size, and configuration.
- `Elastic Recovery`: Upon worker preemption or failure, replacement worker actors instantiate, parse
  `metadata.json`, and restore their assigned rank shards to resume training without loss of progress.

Your Task:
- In `save_sharded_checkpoint(checkpoint_dir, step, rank, world_size, model_shard, optim_shard, metadata)`:
  - Save `model_shard` to `checkpoint_dir/rank_{rank}_model.pt` via `torch.save`.
  - Save `optim_shard` to `checkpoint_dir/rank_{rank}_optim.pt` via `torch.save`.
  - If `rank == 0`, write `metadata.json` containing `step`, `world_size`, and extra `metadata`.
  - Return the path to `model_file`.
- In `load_sharded_checkpoint(checkpoint_dir, rank)`:
  - Read `checkpoint_dir/metadata.json` to extract `step` and `meta_content`.
  - Load `model_shard` from `rank_{rank}_model.pt` and `optim_shard` from `rank_{rank}_optim.pt`.
  - Return `(step, model_shard, optim_shard, meta_content)`.
- In `ShardedTrainWorker.save_checkpoint(checkpoint_dir, metadata)`:
  - Extract `model_shard = {"weight_shard": self.weight_shard.data.clone()}` and optimizer state dict.
  - Call `save_sharded_checkpoint(...)` and return the result.
- In `ShardedTrainWorker.restore_checkpoint(checkpoint_dir)`:
  - Call `load_sharded_checkpoint(checkpoint_dir, self.rank)`.
  - Restore `self.weight_shard.data`, optimizer state dict, and update `self.step_idx`.
  - Return `self.step_idx`.
"""

import json
import os
import tempfile
from typing import Any

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
import torch
import torch.nn as nn
import torch.optim as optim


def save_sharded_checkpoint(
    checkpoint_dir: str,
    step: int,
    rank: int,
    world_size: int,
    model_shard: dict[str, torch.Tensor],
    optim_shard: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> str:
    """Save rank-local sharded model state, optimizer state, and atomic metadata."""
    # TODO: Create checkpoint_dir, save per-rank model/optim tensors, and write metadata.json on rank 0
    pass


def load_sharded_checkpoint(
    checkpoint_dir: str, rank: int
) -> tuple[int, dict[str, torch.Tensor], dict[str, Any], dict[str, Any]]:
    """Load rank-local model and optimizer shards alongside global checkpoint metadata."""
    # TODO: Read metadata.json, load rank_{rank}_model.pt and rank_{rank}_optim.pt, return (step, model, optim, meta)
    pass


@ray.remote
class ShardedTrainWorker:
    """Ray actor holding a sharded parameter slice, supporting atomic checkpointing and recovery."""

    def __init__(self, rank: int, world_size: int, shard_dim: int = 16, lr: float = 0.05) -> None:
        self.rank = rank
        self.world_size = world_size
        self.step_idx = 0
        self.lr = lr

        # Parameter shard initialized deterministically
        self.weight_shard = nn.Parameter(torch.full((shard_dim, 1), 2.0, dtype=torch.float32))
        self.optimizer = optim.SGD([self.weight_shard], lr=lr)

    def train_step(self, x_shard: torch.Tensor, target: torch.Tensor) -> float:
        """Perform a local optimization step on the parameter shard."""
        self.step_idx += 1
        self.optimizer.zero_grad()
        pred = torch.matmul(x_shard, self.weight_shard)
        loss = nn.MSELoss()(pred, target)
        loss.backward()
        self.optimizer.step()
        return float(loss.item())

    def save_checkpoint(self, checkpoint_dir: str, metadata: dict[str, Any] | None = None) -> str:
        """Save local shard state to shared checkpoint directory."""
        # TODO: Save local shard model and optimizer states via save_sharded_checkpoint
        pass

    def restore_checkpoint(self, checkpoint_dir: str) -> int:
        """Restore local shard state and optimizer state from checkpoint directory."""
        # TODO: Load checkpoint via load_sharded_checkpoint, copy to self.weight_shard, load optim state, set step_idx
        pass

    def get_state(self) -> dict[str, Any]:
        """Return current worker rank, step, and weight shard."""
        return {
            "rank": self.rank,
            "step": self.step_idx,
            "weight_shard": self.weight_shard.data.clone(),
        }


def simulate_preemption_and_recovery(
    checkpoint_dir: str,
    total_steps: int = 10,
    checkpoint_at_step: int = 4,
    preempt_at_step: int = 5,
) -> tuple[list[float], list[float]]:
    """Simulate training, checkpointing, worker preemption/failure, and elastic recovery."""
    world_size = 2
    shard_dim = 16

    # 1. Initial worker group
    workers = [
        ShardedTrainWorker.remote(rank=i, world_size=world_size, shard_dim=shard_dim, lr=0.05)
        for i in range(world_size)
    ]

    torch.manual_seed(42)
    x_shards = [torch.randn(8, shard_dim) for _ in range(world_size)]
    target = torch.zeros(8, 1)

    initial_losses: list[float] = []

    # Train until step 4 and take checkpoint
    for step in range(1, preempt_at_step):
        losses = ray.get(
            [workers[i].train_step.remote(x_shards[i], target) for i in range(world_size)]
        )
        initial_losses.append(float(losses[0]))
        if step == checkpoint_at_step:
            ray.get(
                [
                    workers[i].save_checkpoint.remote(checkpoint_dir, {"saved_at_step": step})
                    for i in range(world_size)
                ]
            )

    # 2. Simulate node failure / preemption: Terminate workers
    for w in workers:
        ray.kill(w)

    # 3. Elastic Recovery: Spawn new worker group
    recovered_workers = [
        ShardedTrainWorker.remote(rank=i, world_size=world_size, shard_dim=shard_dim, lr=0.05)
        for i in range(world_size)
    ]

    # Restore from checkpoint
    restored_steps = ray.get(
        [w.restore_checkpoint.remote(checkpoint_dir) for w in recovered_workers]
    )
    for restored_step in restored_steps:
        assert restored_step == checkpoint_at_step, (
            f"Expected restored step {checkpoint_at_step}, got {restored_step}"
        )

    # 4. Resume training from step (checkpoint_at_step + 1) to total_steps
    resumed_losses: list[float] = []
    for _ in range(checkpoint_at_step + 1, total_steps + 1):
        losses = ray.get(
            [recovered_workers[i].train_step.remote(x_shards[i], target) for i in range(world_size)]
        )
        resumed_losses.append(float(losses[0]))

    return initial_losses, resumed_losses


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        checkpoint_dir = os.path.join(temp_dir, "fsdp_ckpt")
        init_losses, resumed_losses = simulate_preemption_and_recovery(
            checkpoint_dir=checkpoint_dir,
            total_steps=10,
            checkpoint_at_step=4,
            preempt_at_step=5,
        )

        # Verify checkpoint files exist
        assert os.path.exists(os.path.join(checkpoint_dir, "metadata.json")), (
            "metadata.json missing"
        )
        assert os.path.exists(os.path.join(checkpoint_dir, "rank_0_model.pt")), (
            "rank_0_model.pt missing"
        )
        assert os.path.exists(os.path.join(checkpoint_dir, "rank_1_model.pt")), (
            "rank_1_model.pt missing"
        )

        # Verify loss progression
        assert len(init_losses) == 4, f"Expected 4 initial steps, got {len(init_losses)}"
        assert len(resumed_losses) == 6, f"Expected 6 resumed steps, got {len(resumed_losses)}"
        assert resumed_losses[-1] < init_losses[0], (
            f"Final loss ({resumed_losses[-1]:.4f}) not lower than start ({init_losses[0]:.4f})"
        )

        print(
            f"✓ fsdp04 verified: Distributed checkpoint saved at step 4, simulated preemption at step 5, "
            f"recovered cleanly and completed through step 10 (loss: {init_losses[0]:.4f} -> {resumed_losses[-1]:.4f})!"
        )

    ray.shutdown()


if __name__ == "__main__":
    verify()
