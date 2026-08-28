"""Chapter 9: Distributed ML Primitives from Scratch - Solution 2: Synchronous Gradient Averaging.

Reference Solution for ml_scratch02.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import numpy as np
import ray


@ray.remote
class WorkerTrainer:
    def __init__(self, rank: int, data_x: list[float], data_y: list[float]) -> None:
        self.rank = rank
        self.data_x = data_x
        self.data_y = data_y

    def compute_gradient(self, w: float) -> float:
        grads = [2.0 * (w * x - y) * x for x, y in zip(self.data_x, self.data_y)]
        return float(np.mean(grads))


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    w0 = WorkerTrainer.remote(0, [1.0, 2.0], [2.0, 4.0])
    w1 = WorkerTrainer.remote(1, [3.0, 4.0], [6.0, 8.0])

    weight = 0.0
    grad_refs = [w0.compute_gradient.remote(weight), w1.compute_gradient.remote(weight)]
    grads = ray.get(grad_refs)
    avg_grad = float(np.mean(grads))
    updated_weight = weight - 0.05 * avg_grad

    assert len(grads) == 2, f"Expected 2 worker gradients, got {len(grads)}"
    assert updated_weight > 0.0, f"Expected updated weight > 0, got {updated_weight}"
    print(
        f"✓ ml_scratch02 verified: Synchronous gradient barrier averaged {len(grads)} workers (new_weight={updated_weight:.4f})!"
    )


if __name__ == "__main__":
    verify()
