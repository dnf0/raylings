# I AM NOT DONE
"""Chapter 2: Distributed State & Actors - Exercise 5: Threaded Actors for Blocking I/O.

In the previous exercise, we used `async def` for non-blocking coroutines.
However, what if your actor methods call legacy synchronous libraries or blocking C-extensions
that do NOT support Python's `async/await` (e.g. `time.sleep`, synchronous DB drivers, OpenCV)?

Ray provides Threaded Actors for this use case:
If you define standard synchronous `def` methods (without `async`) AND specify
`@ray.remote(max_concurrency=N)`, Ray spawns a Python ThreadPool inside the actor process
to handle up to `N` method invocations concurrently!

Key Concepts:
1. `max_concurrency=N` + `async def` -> Coroutine concurrency on a single thread event loop.
2. `max_concurrency=N` + `def` (synchronous) -> Thread-based concurrency via a worker thread pool.
3. Thread Safety: When using threaded actors with synchronous methods mutating shared `self.state`,
   standard threading locks (`threading.Lock`) should be used if modifying shared data structures.

Your Task:
- Define `@ray.remote(max_concurrency=4) class ThreadedComputeActor:`.
- Implement synchronous `def blocking_task(self, task_id: int, duration: float) -> int` using `time.sleep(duration)`.
- Dispatch 4 blocking calls concurrently.
- Verify that execution runs in parallel across the actor's thread pool in < 0.20s.
"""

import threading
import time  # noqa: F401
import ray


# TODO: Decorate class with @ray.remote(max_concurrency=4)
class ThreadedComputeActor:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.completed_tasks: list[int] = []

    # Synchronous def executed in a thread pool
    def blocking_task(self, task_id: int, duration: float) -> int:
        # TODO: Sleep for duration
        # time.sleep(duration)
        # with self.lock:
        #     self.completed_tasks.append(task_id)
        # return task_id * 10
        pass

    def get_completed(self) -> list[int]:
        with self.lock:
            return list(self.completed_tasks)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Instantiate ThreadedComputeActor
    # actor = ThreadedComputeActor.remote()
    # ray.get(actor.get_completed.remote())  # Warm-up actor process
    # start = time.perf_counter()
    # refs = [actor.blocking_task.remote(i, 0.08) for i in range(4)]
    # results = ray.get(refs)
    # elapsed = time.perf_counter() - start
    # completed = ray.get(actor.get_completed.remote())
    results, elapsed, completed = None, 999.0, []

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
