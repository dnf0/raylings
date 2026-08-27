"""Chapter 16: DeepSpeed & PyTorch FSDP - Exercise 2: DeepSpeed ZeRO-1 / ZeRO-2 / ZeRO-3 Memory Partitioning.

DeepSpeed ZeRO (Zero Redundancy Optimizer) eliminates memory redundancies across distributed data-parallel
workers by partitioning optimizer states (ZeRO-1), gradients (ZeRO-2), and model parameters (ZeRO-3).

Key Concepts:
- `ZeRO-1 (Pos)`: Partitions optimizer states across $N$ ranks ($1/N$ optimizer state memory per worker).
- `ZeRO-2 (Pos+g)`: Partitions optimizer states AND gradients across $N$ ranks. Workers use `ReduceScatter`
  to aggregate and partition gradients during backward pass.
- `ZeRO-3 (Pos+g+p)`: Partitions optimizer states, gradients, AND model parameters across $N$ ranks.
  Workers use `AllGather` to reconstruct parameters on-the-fly during forward/backward passes.
- `Collective Communication`:
  - `ReduceScatter`: Sums/averages gradients across ranks and scatters the respective shard to each worker.
  - `AllGather`: Collects sharded parameters from each worker and concatenates into full tensor.

Your Task:
- In `calculate_zero_memory(num_params, world_size, stage, bytes_per_param)`:
  - Calculate per-worker memory requirements for parameters, gradients, and optimizer states across ZeRO stages 0, 1, 2, 3.
  - Return a dictionary with keys `"params"`, `"gradients"`, `"opt_states"`, and `"total"`.
- In `ZeROWorker.step(grad_shard)`:
  - Update local Adam 1st moment ($m$) and 2nd moment ($v$) buffers with `grad_shard`.
  - Apply bias corrections $m_{hat} = m / (1 - \beta_1^t)$ and $v_{hat} = v / (1 - \beta_2^t)$.
  - Update `self.param_shard` in-place and return the updated shard.
- In `reduce_scatter(worker_grads, world_size)`:
  - Compute the mean gradient across all `worker_grads`.
  - Split the averaged gradient into `world_size` equal shards and return the list of shards.
- In `zero_stage3_distributed_step(workers, worker_grads)`:
  - Reduce-scatter `worker_grads` across `workers`.
  - Invoke `.step.remote(grad_shard)` on each worker actor.
  - Fetch results with `ray.get()` and all-gather the shards into the full updated parameter tensor.
"""

# I AM NOT DONE
import os
from typing import Any

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import numpy as np
import ray


def calculate_zero_memory(
    num_params: int, world_size: int, stage: int, bytes_per_param: int = 4
) -> dict[str, float]:
    """Calculate per-worker memory breakdown for ZeRO stages 0, 1, 2, and 3.

    Memory components (FP32 baseline with Adam optimizer):
    - Parameters: num_params * bytes_per_param
    - Gradients: num_params * bytes_per_param
    - Optimizer States (Adam: FP32 master weights + momentum + variance): 3 * num_params * bytes_per_param
    """
    # TODO: Calculate p, g, o according to stage (0, 1, 2, or 3) and world_size
    pass


@ray.remote
class ZeROWorker:
    """Ray actor representing a ZeRO-3 worker holding a shard of parameters and optimizer states."""

    def __init__(
        self,
        rank: int,
        world_size: int,
        param_shard: np.ndarray,
        lr: float = 0.01,
        beta1: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
    ) -> None:
        self.rank = rank
        self.world_size = world_size
        self.param_shard = param_shard.copy()
        self.m = np.zeros_like(param_shard)
        self.v = np.zeros_like(param_shard)
        self.step_count = 0
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps

    def get_param_shard(self) -> np.ndarray:
        """Return the current local parameter shard."""
        return self.param_shard

    def step(self, grad_shard: np.ndarray) -> np.ndarray:
        """Execute local Adam optimizer update on local parameter and optimizer state partition."""
        # TODO: Update m, v, compute bias corrections, update self.param_shard, and return it
        pass


def all_gather(shards: list[np.ndarray]) -> np.ndarray:
    """Gather and concatenate parameter shards from all workers into a full parameter tensor."""
    return np.concatenate(shards, axis=0)


def reduce_scatter(worker_grads: list[np.ndarray], world_size: int) -> list[np.ndarray]:
    """Reduce (average) gradients across workers and scatter into equal shards for each rank."""
    # TODO: Average worker_grads across workers and split into world_size shards
    pass


def zero_stage3_distributed_step(workers: list[Any], worker_grads: list[np.ndarray]) -> np.ndarray:
    """Orchestrate a ZeRO-3 distributed optimizer step across Ray worker actors."""
    # TODO: Reduce-scatter gradients, dispatch step to each worker actor, and all-gather updated shards
    pass


def monolithic_adam_step(
    params: np.ndarray,
    avg_grad: np.ndarray,
    m: np.ndarray,
    v: np.ndarray,
    step_count: int,
    lr: float = 0.01,
    beta1: float = 0.9,
    beta2: float = 0.999,
    eps: float = 1e-8,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Single-process baseline Adam step on full parameters."""
    m_new = beta1 * m + (1.0 - beta1) * avg_grad
    v_new = beta2 * v + (1.0 - beta2) * (avg_grad**2)

    m_hat = m_new / (1.0 - beta1**step_count)
    v_hat = v_new / (1.0 - beta2**step_count)

    params_new = params - lr * m_hat / (np.sqrt(v_hat) + eps)
    return params_new, m_new, v_new


def verify() -> None:
    # 1. Verify ZeRO memory reduction formulas
    num_params = 1_000_000_000  # 1 Billion parameters
    world_size = 8

    m0 = calculate_zero_memory(num_params, world_size, stage=0)
    m1 = calculate_zero_memory(num_params, world_size, stage=1)
    m2 = calculate_zero_memory(num_params, world_size, stage=2)
    m3 = calculate_zero_memory(num_params, world_size, stage=3)

    assert m0 is not None and m1 is not None and m2 is not None and m3 is not None, (
        "calculate_zero_memory returned None"
    )

    assert m3["total"] < m2["total"] < m1["total"] < m0["total"], (
        f"Expected monotonic memory reduction: m3={m3['total']}, m2={m2['total']}, "
        f"m1={m1['total']}, m0={m0['total']}"
    )

    # Check exact memory savings against theoretical values (in GB)
    assert np.isclose(m0["total"] / 1e9, 20.0), (
        f"ZeRO-0 total expected 20.0GB, got {m0['total'] / 1e9}"
    )
    assert np.isclose(m1["total"] / 1e9, 9.5), (
        f"ZeRO-1 total expected 9.5GB, got {m1['total'] / 1e9}"
    )
    assert np.isclose(m2["total"] / 1e9, 6.0), (
        f"ZeRO-2 total expected 6.0GB, got {m2['total'] / 1e9}"
    )
    assert np.isclose(m3["total"] / 1e9, 2.5), (
        f"ZeRO-3 total expected 2.5GB, got {m3['total'] / 1e9}"
    )

    # 2. Verify ZeRO-3 distributed actor communication vs monolithic Adam
    ray.init(ignore_reinit_error=True)

    rng = np.random.default_rng(42)
    p_size = 128
    num_workers = 4
    num_steps = 5
    lr = 0.02

    initial_params = rng.standard_normal(p_size).astype(np.float32)
    param_shards = np.split(initial_params, num_workers)

    workers = [
        ZeROWorker.remote(
            rank=i,
            world_size=num_workers,
            param_shard=param_shards[i],
            lr=lr,
        )
        for i in range(num_workers)
    ]

    # Initialize monolithic baseline state
    baseline_params = initial_params.copy()
    m_base = np.zeros_like(baseline_params)
    v_base = np.zeros_like(baseline_params)

    for step_idx in range(1, num_steps + 1):
        # Simulate different local gradients on each data-parallel worker
        worker_grads = [rng.standard_normal(p_size).astype(np.float32) for _ in range(num_workers)]

        # ZeRO distributed step
        zero_updated_params = zero_stage3_distributed_step(workers, worker_grads)
        assert zero_updated_params is not None, "zero_stage3_distributed_step returned None"

        # Baseline step
        avg_grad = np.mean(worker_grads, axis=0)
        baseline_params, m_base, v_base = monolithic_adam_step(
            baseline_params, avg_grad, m_base, v_base, step_count=step_idx, lr=lr
        )

        assert np.allclose(zero_updated_params, baseline_params, atol=1e-6), (
            f"Step {step_idx}: ZeRO parameter update diverged from baseline!\n"
            f"Max diff: {np.max(np.abs(zero_updated_params - baseline_params))}"
        )

    print(
        "✓ fsdp02 verified: ZeRO memory partitioning (ZeRO-3 saves 87.5% memory) "
        "and 4-worker distributed ZeRO-3 simulation matched monolithic Adam!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
