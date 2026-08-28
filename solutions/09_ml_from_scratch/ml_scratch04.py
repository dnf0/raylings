"""Chapter 9: Distributed ML Primitives from Scratch - Solution 4: Distributed Data-Parallel Trainer.

Reference Solution for ml_scratch04.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import numpy as np
import ray


@ray.remote
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

    w0 = DDPWorker.remote(0, [1.0, 2.0], [3.0, 5.0])
    w1 = DDPWorker.remote(1, [3.0, 4.0], [7.0, 9.0])
    workers = [w0, w1]

    for _ in range(25):
        grad_refs = [w.compute_gradients.remote() for w in workers]
        grads = ray.get(grad_refs)
        avg_gw = sum(g[0] for g in grads) / len(grads)
        avg_gb = sum(g[1] for g in grads) / len(grads)
        ray.get([w.apply_gradients.remote(avg_gw, avg_gb) for w in workers])

    p0 = ray.get(w0.get_params.remote())
    p1 = ray.get(w1.get_params.remote())

    assert abs(p0[0] - 2.0) < 0.2, f"Expected w ~ 2.0, got {p0[0]}"
    assert p0 == p1, f"Expected workers to have identical synchronized weights, got {p0} vs {p1}"
    print(
        f"✓ ml_scratch04 verified: Distributed Data-Parallel training converged to w={p0[0]:.3f}, b={p0[1]:.3f}!"
    )


if __name__ == "__main__":
    verify()
