"""Chapter 2: Distributed State & Actors - Solution 5: Threaded Actors for Blocking I/O.

Reference Solution for actors05.
"""

import threading
import time

import ray


@ray.remote(max_concurrency=4)
class ThreadedComputeActor:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.completed_tasks: list[int] = []

    def blocking_task(self, task_id: int, duration: float) -> int:
        time.sleep(duration)
        with self.lock:
            self.completed_tasks.append(task_id)
        return task_id * 10

    def get_completed(self) -> list[int]:
        with self.lock:
            return list(self.completed_tasks)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    actor = ThreadedComputeActor.remote()
    ray.get(actor.get_completed.remote())  # Warm-up actor process
    start = time.perf_counter()
    refs = [actor.blocking_task.remote(i, 0.08) for i in range(4)]
    results = ray.get(refs)
    elapsed = time.perf_counter() - start
    completed = ray.get(actor.get_completed.remote())

    expected = [0, 10, 20, 30]
    assert results == expected, f"Expected {expected}, got {results}"
    assert len(completed) == 4, f"Expected 4 completed tasks, got {len(completed)}"
    print(f"Elapsed time for 4 concurrent blocking tasks: {elapsed:.3f}s")
    assert elapsed < 0.22, (
        f"Threaded actor took too long ({elapsed:.3f}s), thread pool concurrency not active"
    )
    print("✓ actors05 verified: Threaded Actor multi-thread concurrency confirmed!")


if __name__ == "__main__":
    verify()
