"""Chapter 16: DeepSpeed & PyTorch FSDP - Solution 2: DeepSpeed ZeRO-1 / ZeRO-2 / ZeRO-3 Memory Partitioning.

Reference Solution for fsdp02.
"""

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
    p_full = float(num_params * bytes_per_param)
    g_full = float(num_params * bytes_per_param)
    o_full = float(3 * num_params * bytes_per_param)

    if stage == 0:
        # Standard Data Parallel (full redundancy)
        p = p_full
        g = g_full
        o = o_full
    elif stage == 1:
        # ZeRO-1 (Pos): Partition Optimizer States
        p = p_full
        g = g_full
        o = o_full / world_size
    elif stage == 2:
        # ZeRO-2 (Pos+g): Partition Optimizer States + Gradients
        p = p_full
        g = g_full / world_size
        o = o_full / world_size
    elif stage == 3:
        # ZeRO-3 (Pos+g+p): Partition Optimizer States + Gradients + Parameters
        p = p_full / world_size
        g = g_full / world_size
        o = o_full / world_size
    else:
        raise ValueError(f"Invalid ZeRO stage: {stage}. Expected 0, 1, 2, or 3.")

    return {
        "params": p,
        "gradients": g,
        "opt_states": o,
        "total": p + g + o,
    }


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
        self.step_count += 1
        self.m = self.beta1 * self.m + (1.0 - self.beta1) * grad_shard
        self.v = self.beta2 * self.v + (1.0 - self.beta2) * (grad_shard**2)

        m_hat = self.m / (1.0 - self.beta1**self.step_count)
        v_hat = self.v / (1.0 - self.beta2**self.step_count)

        self.param_shard = self.param_shard - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
        return self.param_shard


def all_gather(shards: list[np.ndarray]) -> np.ndarray:
    """Gather and concatenate parameter shards from all workers into a full parameter tensor."""
    return np.concatenate(shards, axis=0)


def reduce_scatter(worker_grads: list[np.ndarray], world_size: int) -> list[np.ndarray]:
    """Reduce (average) gradients across workers and scatter into equal shards for each rank."""
    avg_grad = np.mean(worker_grads, axis=0)
    shards: list[np.ndarray] = np.split(avg_grad, world_size)
    return shards


def zero_stage3_distributed_step(workers: list[Any], worker_grads: list[np.ndarray]) -> np.ndarray:
    """Orchestrate a ZeRO-3 distributed optimizer step across Ray worker actors."""
    world_size = len(workers)
    # 1. ReduceScatter: Average full gradients from each worker and slice for each rank
    grad_shards = reduce_scatter(worker_grads, world_size)

    # 2. Dispatch optimizer step to each worker actor
    futures = [worker.step.remote(grad_shards[i]) for i, worker in enumerate(workers)]
    updated_shards = ray.get(futures)

    # 3. AllGather: Reconstruct the full updated parameter tensor
    full_params = all_gather(updated_shards)
    return full_params


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
