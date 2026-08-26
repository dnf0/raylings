# I AM NOT DONE
"""Chapter 9: Distributed ML Primitives from Scratch - Exercise 3: Ring All-Reduce Primitive.

Ring All-Reduce is the algorithm that powers multi-GPU communication libraries like NCCL and Horovod.
Instead of sending all tensors to a central bottleneck node:
1. N workers are arranged in a logical ring (zsh 	o 1 	o 2 	o \dots 	o N-1 	o 0$).
2. Scatter-Reduce Phase (N-1 steps):
   - Each worker sends chunk $ to its neighbor and receives chunk -1$, accumulating into its local buffer.
   - At the end of Scatter-Reduce, each node holds the globally reduced sum for 1 chunk.
3. Allgather Phase (N-1 steps):
   - Each worker circulates its fully-reduced chunk around the ring until all nodes possess all reduced chunks.

Complexity: Independent of cluster size N! Bandwidth per node is  	imes
rac{N-1}{N} 	imes S$,
optimal for large model synchronization.

Your Task:
- Define `@ray.remote` actor `RingWorker(rank: int, world_size: int, data: list[float])`:
  - `get_chunk(self, chunk_idx: int) -> list[float]`
  - `add_chunk(self, chunk_idx: int, chunk_data: list[float]) -> None`
  - `set_chunk(self, chunk_idx: int, chunk_data: list[float]) -> None`
  - `get_buffer(self) -> list[float]`
- Implement `ring_allreduce(workers: list) -> None`.
- In `verify()`:
  - Spawn 3 `RingWorker` actors with buffers `[1.0, 2.0, 3.0]`, `[10.0, 20.0, 30.0]`, and `[100.0, 200.0, 300.0]`.
  - Execute `ring_allreduce(workers)`.
  - Assert that all 3 workers have buffer equal to `[111.0, 222.0, 333.0]`.
"""

import numpy as np
import ray


# TODO: Define RingWorker actor
class RingWorker:
    def __init__(self, rank: int, world_size: int, data: list[float]) -> None:
        self.rank = rank
        self.world_size = world_size
        self.buffer = np.array(data, dtype=np.float32)

    def get_chunk(self, chunk_idx: int) -> list[float]:
        chunk_size = len(self.buffer) // self.world_size
        start = chunk_idx * chunk_size
        return self.buffer[start : start + chunk_size].tolist()

    def add_chunk(self, chunk_idx: int, chunk_data: list[float]) -> None:
        chunk_size = len(self.buffer) // self.world_size
        start = chunk_idx * chunk_size
        self.buffer[start : start + chunk_size] += np.array(chunk_data, dtype=np.float32)

    def set_chunk(self, chunk_idx: int, chunk_data: list[float]) -> None:
        chunk_size = len(self.buffer) // self.world_size
        start = chunk_idx * chunk_size
        self.buffer[start : start + chunk_size] = np.array(chunk_data, dtype=np.float32)

    def get_buffer(self) -> list[float]:
        return self.buffer.tolist()


# TODO: Implement ring_allreduce function
def ring_allreduce(workers: list[ray.actor.ActorHandle]) -> None:
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Initialize 3 RingWorkers and perform ring_allreduce
    # w0 = RingWorker.remote(0, 3, [1.0, 2.0, 3.0])
    # w1 = RingWorker.remote(1, 3, [10.0, 20.0, 30.0])
    # w2 = RingWorker.remote(2, 3, [100.0, 200.0, 300.0])
    # workers = [w0, w1, w2]
    # ring_allreduce(workers)
    # results = ray.get([w.get_buffer.remote() for w in workers])
    results = []

    expected = [111.0, 222.0, 333.0]
    assert len(results) == 3, f"Expected 3 workers, got {len(results)}"
    for r in results:
        assert r == expected, f"Expected {expected}, got {r}"
    print(
        f"✓ ml_scratch03 verified: Ring All-Reduce synchronized {len(results)} workers to {expected}!"
    )


if __name__ == "__main__":
    verify()
