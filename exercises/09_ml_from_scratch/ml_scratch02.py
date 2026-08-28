"""
Exercise: exercises/09_ml_from_scratch/ml_scratch02.py
Topic: Asynchronous Parameter Server Architecture (Hogwild!)

Context & Why:
In heterogeneous clusters where workers have differing speeds, synchronous parameter updates suffer
from the **straggler problem** (fast workers sit idle waiting for the slowest worker).

In **Asynchronous Parameter Servers**, workers pull weights and push gradients independently
without waiting for peers. While gradients may be slightly stale, total training throughput is maximized.

Instructions:
1. Implement asynchronous non-blocking gradient updates on the parameter server.
2. Verify convergence under asynchronous updates.
"""

# I AM NOT DONE

r"""Chapter 9: Distributed ML Primitives from Scratch - Exercise 2: Synchronous Gradient Averaging.

In distributed deep learning:
- Synchronous SGD: The optimizer waits for ALL workers to complete their forward/backward pass,
  averages their gradient vectors, and updates the weights at a synchronization barrier.
  This ensures deterministic, mathematically exact gradient descent.
- Asynchronous SGD: Workers update weights independently without waiting for peers (can suffer from stale gradients).

Pattern for Synchronous Barrier:
```python
# 1. Broadcast latest weights to all workers
weight_ref = ray.put(current_weights)

# 2. Dispatch gradient computation across workers
grad_refs = [worker.compute_gradient.remote(weight_ref, batch) for worker, batch in zip(workers, shards)]

# 3. Synchronous Barrier: wait for all gradients
all_grads = ray.get(grad_refs)

# 4. Average gradients across workers
avg_grad = np.mean(all_grads, axis=0)
```

Your Task:
- Define `@ray.remote` actor `WorkerTrainer(rank: int, data_x: list[float], data_y: list[float])`:
  - Method `compute_gradient(self, w: float) -> float`:
    - Computes average gradient over local data points: `np.mean([2 * (w * x - y) * x for x, y in zip(self.data_x, self.data_y)])`.
- In `verify()`:
  - Create 2 workers:
    - Worker 0: data_x = [1.0, 2.0], data_y = [2.0, 4.0] (target slope = 2.0)
    - Worker 1: data_x = [3.0, 4.0], data_y = [6.0, 8.0] (target slope = 2.0)
  - Perform 1 synchronous step starting with  = 0.0$:
    - Compute gradients on both workers simultaneously.
    - Synchronously collect and average both gradients.
    - Update  = w - 0.05 \cdot avg\_grad$.
  - Assert that after 1 step,  > 0.0$ and worker gradients were averaged correctly.
"""

import numpy as np
import ray


# TODO: Define WorkerTrainer actor
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

    # TODO: Instantiate 2 WorkerTrainers
    # w0 = WorkerTrainer.remote(0, [1.0, 2.0], [2.0, 4.0])
    # w1 = WorkerTrainer.remote(1, [3.0, 4.0], [6.0, 8.0])

    # TODO: Compute gradients synchronously
    # weight = 0.0
    # grad_refs = [w0.compute_gradient.remote(weight), w1.compute_gradient.remote(weight)]
    # grads = ray.get(grad_refs)
    # avg_grad = float(np.mean(grads))
    # updated_weight = weight - 0.05 * avg_grad
    grads, updated_weight = [], 0.0

    assert len(grads) == 2, f"Expected 2 worker gradients, got {len(grads)}"
    assert updated_weight > 0.0, f"Expected updated weight > 0, got {updated_weight}"
    print(
        f"✓ ml_scratch02 verified: Synchronous gradient barrier averaged {len(grads)} workers (new_weight={updated_weight:.4f})!"
    )


if __name__ == "__main__":
    verify()
