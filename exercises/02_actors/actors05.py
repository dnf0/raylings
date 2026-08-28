"""
Exercise: exercises/02_actors/actors05.py
Topic: Threaded Actors for Blocking Synchronous I/O

Context & Why:
While `async def` works for non-blocking coroutines, legacy Python libraries and C-extensions
often make synchronous blocking calls (e.g. OpenCV image processing, blocking DB drivers, `time.sleep`).

Ray supports **Threaded Actors**:
If you define standard synchronous `def` methods (without `async`) AND specify
`@ray.remote(max_concurrency=N)`, Ray provisions an internal `ThreadPool` inside the actor process
to handle up to `N` synchronous invocations concurrently across multiple OS threads.

Instructions:
1. Define `@ray.remote(max_concurrency=4) class ThreadedComputeActor:`.
2. Implement synchronous `blocking_task` using `time.sleep(duration)`.
3. Verify that 4 concurrent tasks execute in parallel on the threaded actor.
"""

# I AM NOT DONE

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
    assert elapsed < 0.30, (
        f"Threaded actor took too long ({elapsed:.3f}s), thread pool concurrency not active"
    )
    print("✓ actors05 verified: Threaded Actor multi-thread concurrency confirmed!")


if __name__ == "__main__":
    verify()
