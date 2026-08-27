"""Chapter 9: Distributed ML Primitives from Scratch - Solution 1: Distributed Parameter Server.

Reference Solution for ml_scratch01.
"""

import numpy as np
import ray


@ray.remote
class ParameterServer:
    def __init__(self, dim: int, lr: float = 0.1) -> None:
        self.weights = np.zeros(dim, dtype=np.float32)
        self.lr = lr

    def get_weights(self) -> list[float]:
        return self.weights.tolist()

    def apply_gradient(self, grad: list[float]) -> list[float]:
        self.weights -= self.lr * np.array(grad, dtype=np.float32)
        return self.weights.tolist()


@ray.remote
def compute_gradient(weights: list[float], x: float, y: float) -> list[float]:
    w = weights[0]
    pred = w * x
    grad = 2.0 * (pred - y) * x
    return [grad]


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    ps = ParameterServer.remote(dim=1, lr=0.05)
    for _ in range(10):
        w = ray.get(ps.get_weights.remote())
        g = ray.get(compute_gradient.remote(w, 2.0, 4.0))
        ray.get(ps.apply_gradient.remote(g))

    final_weight = ray.get(ps.get_weights.remote())

    assert abs(final_weight[0] - 2.0) < 0.1, f"Expected weight ~2.0, got {final_weight[0]}"
    print(f"✓ ml_scratch01 verified: ParameterServer converged to {final_weight[0]:.4f}!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
