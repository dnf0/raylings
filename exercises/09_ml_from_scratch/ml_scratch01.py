r"""Chapter 9: Distributed ML Primitives from Scratch - Exercise 1: Distributed Parameter Server.

The Parameter Server (PS) architecture is a fundamental distributed training pattern.
It decouples model storage from computation:
- ParameterServer Actor: Stores global model parameters, serves the latest weights to workers,
  and updates weights using incoming gradients.
- Worker Tasks: Fetch the latest weights, compute loss and gradients on local data batches,
  and push gradient vectors back to the server.

```python
@ray.remote
class ParameterServer:
    def __init__(self, dim: int, lr: float = 0.1):
        self.weights = np.zeros(dim)
        self.lr = lr

    def get_weights(self) -> np.ndarray:
        return self.weights

    def update_gradients(self, grad: np.ndarray) -> np.ndarray:
        self.weights -= self.lr * grad
        return self.weights
```

Your Task:
- Define `@ray.remote` actor `ParameterServer(dim: int, lr: float = 0.1)`:
  - `get_weights(self) -> list[float]`: returns list of weights.
  - `apply_gradient(self, grad: list[float]) -> list[float]`: subtracts `self.lr * grad` from weights and returns updated weights.
- Define `@ray.remote` task `compute_gradient(weights: list[float], batch_x: float, batch_y: float) -> list[float]`:
  - Computes gradient of MSE loss for  = w \cdot x$:
     = w \cdot x$
     = 2 \cdot (pred - y) \cdot x$
  - Returns `[grad]` for 1D scalar parameter.
- In `verify()`:
  - Initialize `ParameterServer` with `dim=1, lr=0.05`.
  - In a loop of 10 steps:
    - Get weights from server.
    - Compute gradient on sample =2.0, y=4.0$.
    - Push gradient to server.
  - Verify that the final learned weight approaches 2.0 (assert `abs(final_weight[0] - 2.0) < 0.1`).
"""

import numpy as np
import ray


# TODO: Define ParameterServer actor
class ParameterServer:
    def __init__(self, dim: int, lr: float = 0.1) -> None:
        self.weights = np.zeros(dim, dtype=np.float32)
        self.lr = lr

    def get_weights(self) -> list[float]:
        return self.weights.tolist()

    def apply_gradient(self, grad: list[float]) -> list[float]:
        self.weights -= self.lr * np.array(grad, dtype=np.float32)
        return self.weights.tolist()


# TODO: Define compute_gradient remote task
def compute_gradient(weights: list[float], x: float, y: float) -> list[float]:
    w = weights[0]
    pred = w * x
    grad = 2.0 * (pred - y) * x
    return [grad]


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Train ParameterServer for 10 steps
    # ps = ParameterServer.remote(dim=1, lr=0.05)
    # for _ in range(10):
    #     w = ray.get(ps.get_weights.remote())
    #     g = ray.get(compute_gradient.remote(w, 2.0, 4.0))
    #     ray.get(ps.apply_gradient.remote(g))
    # final_weight = ray.get(ps.get_weights.remote())
    final_weight = [0.0]

    assert abs(final_weight[0] - 2.0) < 0.1, f"Expected weight ~2.0, got {final_weight[0]}"
    print(f"✓ ml_scratch01 verified: ParameterServer converged to {final_weight[0]:.4f}!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
