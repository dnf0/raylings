# I AM NOT DONE
"""Chapter 2: Distributed State & Actors - Exercise 3: Passing Actor Handles.

In Ray, `ActorHandle`s can be passed as arguments to other `@ray.remote` tasks or actors.
When a worker receives an `ActorHandle`, it can invoke methods on that actor directly!

This pattern is widely used for:
1. Distributed Aggregators: Multiple worker tasks sending intermediate metrics/results
   to a single centralized actor.
2. Progress Tracking: Long-running tasks reporting step completions to a dashboard actor.
3. Coordination & Barrier Synchronization across distributed workers.

Example:
    @ray.remote
    class ProgressTracker:
        def __init__(self): self.completed = 0
        def report(self): self.completed += 1

    @ray.remote
    def worker(tracker_handle, worker_id):
        # Do work...
        tracker_handle.report.remote()

Your Task:
- Define a `@ray.remote` class `MetricsLogger` with:
  - `log(worker_id: str, count: int) -> None`: records `count` items processed by `worker_id` in a dictionary `self.records`.
  - `get_total() -> int`: returns the sum of all counts recorded.
- Define a `@ray.remote` function `process_batch(logger_handle, worker_id: str, items: list[int]) -> int`:
  - Computes `sum(items)`
  - Calls `logger_handle.log.remote(worker_id, len(items))`
  - Returns `sum(items)`
- Launch 3 worker tasks in parallel with different batches, wait for them to finish, and assert total logged count is 9.
"""

import ray
from ray.actor import ActorHandle


# TODO: Define MetricsLogger actor
class MetricsLogger:
    def __init__(self) -> None:
        self.records: dict[str, int] = {}

    def log(self, worker_id: str, count: int) -> None:
        self.records[worker_id] = self.records.get(worker_id, 0) + count

    def get_total(self) -> int:
        return sum(self.records.values())


# TODO: Define process_batch remote task
def process_batch(logger: ActorHandle, worker_id: str, items: list[int]) -> int:
    total = sum(items)
    # TODO: Log items processed to logger
    # logger.log.remote(worker_id, len(items))
    return total


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Instantiate MetricsLogger actor
    # logger = MetricsLogger.remote()

    # TODO: Launch 3 process_batch tasks passing logger handle
    # batches = [
    #     ("worker_1", [1, 2, 3]),
    #     ("worker_2", [4, 5]),
    #     ("worker_3", [6, 7, 8, 9]),
    # ]
    # task_refs = [process_batch.remote(logger, wid, items) for wid, items in batches]
    # batch_sums = ray.get(task_refs)
    # total_items_logged = ray.get(logger.get_total.remote())
    batch_sums, total_items_logged = None, None

    assert batch_sums == [6, 9, 30], f"Expected batch sums [6, 9, 30], got {batch_sums}"
    assert total_items_logged == 9, f"Expected 9 total items logged, got {total_items_logged}"
    print(f"✓ actors03 verified: Actor handle passed across distributed worker tasks (total={total_items_logged})!")


if __name__ == "__main__":
    verify()
