"""Chapter 15: Distributed LLM Serving & vLLM - Exercise 1: Tensor Parallelism & Worker Actor Groups.

Tensor Parallelism (TP) partitions individual weight matrices across multiple worker actors
to fit large model layers across GPU/node memory and parallelize matrix multiplication.

Key Concepts:
- `ColumnParallelLinear`: Shards the weight matrix along columns (output dimension).
  Each worker computes `X @ W1_shard`, producing a slice of the hidden activation.
- `RowParallelLinear`: Shards the weight matrix along rows (input dimension).
  Each worker takes its slice of the hidden activation and computes `H_shard @ W2_shard`.
- `All-Reduce (Sum)`: Sums partial outputs across all TP workers to recover the full layer output:
  `Output = sum(H_shard_i @ W2_shard_i) == X @ W1 @ W2`.

Your Task:
- In `shard_weights(w1, w2, world_size)`:
  - Split `w1` column-wise (axis 1) across `world_size` workers.
  - Split `w2` row-wise (axis 0) across `world_size` workers.
- In `TPWorker.forward(x)`:
  - Compute local column-parallel projection `h_shard = x @ self.w1_shard`.
  - Compute local row-parallel projection `z_shard = h_shard @ self.w2_shard`.
  - Return `z_shard`.
- In `tensor_parallel_forward(workers, x)`:
  - Invoke `.forward.remote(x)` on each worker in `workers`.
  - Retrieve results via `ray.get()`.
  - All-reduce (sum) the outputs across all workers along axis 0.
"""

# I AM NOT DONE
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
        # TODO: Compute column projection and row projection locally
        pass


def shard_weights(
    w1: np.ndarray, w2: np.ndarray, world_size: int
) -> list[tuple[np.ndarray, np.ndarray]]:
    # TODO: Shard W1 column-wise (axis 1) and W2 row-wise (axis 0)
    pass


def tensor_parallel_forward(workers: list[Any], x: np.ndarray) -> np.ndarray:
    # TODO: Dispatch forward pass to workers and all-reduce (sum) outputs
    pass


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
    assert shards is not None, "shard_weights returned None"
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
    assert tp_output is not None, "tensor_parallel_forward returned None"
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
