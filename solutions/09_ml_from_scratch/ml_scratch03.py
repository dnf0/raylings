"""Chapter 9: Distributed ML Primitives from Scratch - Solution 3: Ring All-Reduce Primitive.

Reference Solution for ml_scratch03.
"""

import numpy as np
import ray


@ray.remote
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


def ring_allreduce(workers: list) -> None:
    N = len(workers)
    # 1. Scatter-Reduce Phase
    for step in range(N - 1):
        send_chunks = []
        for i in range(N):
            chunk_idx = (i - step) % N
            send_chunks.append(workers[i].get_chunk.remote(chunk_idx))

        chunks = ray.get(send_chunks)
        add_ops = []
        for i in range(N):
            recv_idx = (i + 1) % N
            chunk_idx = (i - step) % N
            add_ops.append(workers[recv_idx].add_chunk.remote(chunk_idx, chunks[i]))
        ray.get(add_ops)

    # 2. Allgather Phase
    for step in range(N - 1):
        send_chunks = []
        for i in range(N):
            chunk_idx = (i - step + 1) % N
            send_chunks.append(workers[i].get_chunk.remote(chunk_idx))

        chunks = ray.get(send_chunks)
        set_ops = []
        for i in range(N):
            recv_idx = (i + 1) % N
            chunk_idx = (i - step + 1) % N
            set_ops.append(workers[recv_idx].set_chunk.remote(chunk_idx, chunks[i]))
        ray.get(set_ops)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    w0 = RingWorker.remote(0, 3, [1.0, 2.0, 3.0])
    w1 = RingWorker.remote(1, 3, [10.0, 20.0, 30.0])
    w2 = RingWorker.remote(2, 3, [100.0, 200.0, 300.0])
    workers = [w0, w1, w2]

    ring_allreduce(workers)
    results = ray.get([w.get_buffer.remote() for w in workers])

    expected = [111.0, 222.0, 333.0]
    assert len(results) == 3, f"Expected 3 workers, got {len(results)}"
    for r in results:
        assert r == expected, f"Expected {expected}, got {r}"
    print(
        f"✓ ml_scratch03 verified: Ring All-Reduce synchronized {len(results)} workers to {expected}!"
    )


if __name__ == "__main__":
    verify()
