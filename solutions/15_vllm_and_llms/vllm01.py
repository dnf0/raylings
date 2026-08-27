"""Chapter 15: Distributed LLM Serving & vLLM - Solution 1: Tensor Parallelism & Worker Actor Groups.

Reference Solution for vllm01.
"""

import os
from typing import Any

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import numpy as np
import ray


@ray.remote
class TPWorker:
    """Tensor Parallel worker actor holding ColumnParallel and RowParallel weight shards."""

    def __init__(
        self, rank: int, world_size: int, w1_shard: np.ndarray, w2_shard: np.ndarray
    ) -> None:
        self.rank = rank
        self.world_size = world_size
        self.w1_shard = w1_shard  # Shape: [in_features, hidden_features // world_size]
        self.w2_shard = w2_shard  # Shape: [hidden_features // world_size, out_features]

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Compute column projection, followed by row projection."""
        # Local column parallel linear: X @ W1_shard -> [batch, hidden // world_size]
        h_shard = np.matmul(x, self.w1_shard)
        # Local row parallel linear: H_shard @ W2_shard -> [batch, out_features]
        z_shard = np.matmul(h_shard, self.w2_shard)
        return z_shard


def shard_weights(
    w1: np.ndarray, w2: np.ndarray, world_size: int
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Shard W1 column-wise and W2 row-wise across world_size workers."""
    # ColumnParallelLinear shards output dimension (axis 1)
    w1_shards = np.split(w1, world_size, axis=1)
    # RowParallelLinear shards input dimension (axis 0)
    w2_shards = np.split(w2, world_size, axis=0)
    return [(w1_shards[i], w2_shards[i]) for i in range(world_size)]


def tensor_parallel_forward(workers: list[Any], x: np.ndarray) -> np.ndarray:
    """Dispatch input to all TP workers and all-reduce (sum) their partial outputs."""
    futures = [w.forward.remote(x) for w in workers]
    partial_outputs = ray.get(futures)
    # All-reduce: Sum partial outputs across all tensor parallel ranks
    all_reduced: np.ndarray = np.sum(partial_outputs, axis=0)
    return all_reduced


def baseline_forward(x: np.ndarray, w1: np.ndarray, w2: np.ndarray) -> np.ndarray:
    """Monolithic single-process reference forward pass: (X @ W1) @ W2."""
    h = np.matmul(x, w1)
    z: np.ndarray = np.matmul(h, w2)
    return z


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    rng = np.random.default_rng(42)
    batch_size = 4
    in_features = 8
    hidden_features = 16
    out_features = 8
    world_size = 2

    x = rng.standard_normal((batch_size, in_features)).astype(np.float32)
    w1 = rng.standard_normal((in_features, hidden_features)).astype(np.float32)
    w2 = rng.standard_normal((hidden_features, out_features)).astype(np.float32)

    # 1. Compute baseline output on monolithic weights
    baseline = baseline_forward(x, w1, w2)

    # 2. Shard weights across tensor-parallel worker group
    shards = shard_weights(w1, w2, world_size)
    assert len(shards) == world_size, f"Expected {world_size} shards, got {len(shards)}"

    workers = [
        TPWorker.remote(
            rank=i,
            world_size=world_size,
            w1_shard=shards[i][0],
            w2_shard=shards[i][1],
        )
        for i in range(world_size)
    ]

    # 3. Execute distributed tensor parallel forward pass
    tp_output = tensor_parallel_forward(workers, x)

    assert tp_output.shape == baseline.shape, (
        f"Shape mismatch: {tp_output.shape} vs {baseline.shape}"
    )
    assert np.allclose(tp_output, baseline, atol=1e-5), (
        f"Tensor parallel output does not match monolithic baseline!\n"
        f"Max diff: {np.max(np.abs(tp_output - baseline))}"
    )

    print(
        f"✓ vllm01 verified: 2-rank Tensor Parallelism matched baseline (max error: "
        f"{np.max(np.abs(tp_output - baseline)):.2e})!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
