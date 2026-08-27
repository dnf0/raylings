r"""Chapter 9: Distributed ML Primitives from Scratch - Exercise 4: Distributed Data-Parallel Trainer.

In Distributed Data-Parallel (DDP) training:
1. Sharded Data: The dataset is split into N shards across N worker actors.
2. Local Forward / Backward: Each worker computes loss and gradients on its local shard.
3. Gradient Synchronization: Workers average their gradients across the cluster.
4. Local Optimizer Step: Each worker applies the averaged gradient to its local copy of model weights.
   Because all workers apply the exact same averaged gradient, their model weights stay identical!

Your Task:
- Define `@ray.remote` actor `DDPWorker(rank: int, x_data: list[float], y_data: list[float])`:
  - `__init__(self, rank, x_data, y_data)`: Initializes `self.w = 0.0`, `self.b = 0.0`, `self.lr = 0.05`.
  - `compute_gradients(self) -> tuple[float, float]`:
    - Predicts  = w \cdot x + b$.
    - Returns local average gradients  = (	ext{mean}(2(pred - y)x), 	ext{mean}(2(pred - y)))$.
  - `apply_gradients(self, avg_grad_w: float, avg_grad_b: float) -> None`:
    - Updates  = w - lr \cdot avg\_grad\_w$ and  = b - lr \cdot avg\_grad\_b$.
  - `get_params(self) -> tuple[float, float]`: returns `(self.w, self.b)`.
- In `verify()`:
  - Target model:  = 2x + 1$.
  - Worker 0 gets data: =[1.0, 2.0], y=[3.0, 5.0]$.
  - Worker 1 gets data: =[3.0, 4.0], y=[7.0, 9.0]$.
  - Run 25 training epochs with synchronous gradient averaging.
  - Verify that both workers converged close to  pprox 2.0$ and  pprox 1.0$ (assert $	ext{abs}(w - 2.0) < 0.2$).
"""

import numpy as np
import ray


# TODO: Define DDPWorker actor
class DDPWorker:
    def __init__(self, rank: int, x_data: list[float], y_data: list[float]) -> None:
        self.rank = rank
        self.x = np.array(x_data, dtype=np.float32)
        self.y = np.array(y_data, dtype=np.float32)
        self.w = 0.0
        self.b = 0.0
        self.lr = 0.05

    def compute_gradients(self) -> tuple[float, float]:
        preds = self.w * self.x + self.b
        diff = preds - self.y
        gw = float(np.mean(2.0 * diff * self.x))
        gb = float(np.mean(2.0 * diff))
        return gw, gb

    def apply_gradients(self, avg_gw: float, avg_gb: float) -> None:
        self.w -= self.lr * avg_gw
        self.b -= self.lr * avg_gb

    def get_params(self) -> tuple[float, float]:
        return self.w, self.b


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Instantiate 2 DDPWorker actors
    # w0 = DDPWorker.remote(0, [1.0, 2.0], [3.0, 5.0])
    # w1 = DDPWorker.remote(1, [3.0, 4.0], [7.0, 9.0])
    # workers = [w0, w1]

    # TODO: Train for 25 epochs
    # for _ in range(25):
    #     grad_refs = [w.compute_gradients.remote() for w in workers]
    #     grads = ray.get(grad_refs)
    #     avg_gw = sum(g[0] for g in grads) / len(grads)
    #     avg_gb = sum(g[1] for g in grads) / len(grads)
    #     ray.get([w.apply_gradients.remote(avg_gw, avg_gb) for w in workers])

    # p0 = ray.get(w0.get_params.remote())
    # p1 = ray.get(w1.get_params.remote())
    p0, p1 = (0.0, 0.0), (0.0, 0.0)

    assert abs(p0[0] - 2.0) < 0.2, f"Expected w ~ 2.0, got {p0[0]}"
    assert p0 == p1, f"Expected workers to have identical synchronized weights, got {p0} vs {p1}"
    print(
        f"✓ ml_scratch04 verified: Distributed Data-Parallel training converged to w={p0[0]:.3f}, b={p0[1]:.3f}!"
    )


if __name__ == "__main__":
    verify()
