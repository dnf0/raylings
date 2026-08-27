"""Chapter 2: Distributed State & Actors - Exercise 3: Passing Actor Handles.

In Ray, `ActorHandle`s can be passed as arguments to other `@ray.remote` tasks or actors.
When a worker receives an `ActorHandle`, it can invoke methods on that actor directly!

This pattern is widely used for:
1. Distributed Aggregators: Multiple worker actors sending intermediate metrics/results
   to a single centralized actor.
2. Progress Tracking: Long-running actors reporting step completions to a coordinator actor.
3. Coordination & Barrier Synchronization across distributed workers.

Example:
    @ray.remote
    class ProgressTracker:
        def __init__(self): self.completed = 0
        def report(self): self.completed += 1

    @ray.remote
    class Worker:
        def __init__(self, tracker_handle):
            self.tracker = tracker_handle

        def do_work(self):
            ray.get(self.tracker.report.remote())

Your Task:
- Define a `@ray.remote` class `MetricsLogger` with:
  - `log(worker_id: str, count: int) -> None`: records `count` items processed by `worker_id` in a dictionary `self.records`.
  - `get_total() -> int`: returns the sum of all counts recorded.
- Define a `@ray.remote` class `BatchWorker` with:
  - `__init__(self, worker_id: str, logger: ActorHandle) -> None`
  - `process(self, items: list[int]) -> int`:
    - Computes `total = sum(items)`
    - Logs items processed by calling `ray.get(self.logger.log.remote(self.worker_id, len(items)))`
    - Returns `total`
- Create 3 `BatchWorker` actors passing the `MetricsLogger` handle, process batches in parallel, and verify total logged count is 9.
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


# TODO: Define BatchWorker actor
class BatchWorker:
    def __init__(self, worker_id: str, logger: ActorHandle) -> None:
        self.worker_id = worker_id
        self.logger = logger

    def process(self, items: list[int]) -> int:
        # TODO: Compute total and call logger.log
        # total = sum(items)
        # ray.get(self.logger.log.remote(self.worker_id, len(items)))
        # return total
        pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Instantiate MetricsLogger actor
    # logger = MetricsLogger.remote()

    # TODO: Create BatchWorker actors and launch process tasks
    # batches = [
    #     ("worker_1", [1, 2, 3]),
    #     ("worker_2", [4, 5]),
    #     ("worker_3", [6, 7, 8, 9]),
    # ]
    # workers = [BatchWorker.remote(wid, logger) for wid, _ in batches]
    # task_refs = [w.process.remote(items) for w, (_, items) in zip(workers, batches, strict=False)]
    # batch_sums = ray.get(task_refs)
    # total_items_logged = ray.get(logger.get_total.remote())
    batch_sums, total_items_logged = None, None

    assert batch_sums == [6, 9, 30], f"Expected batch sums [6, 9, 30], got {batch_sums}"
    assert total_items_logged == 9, f"Expected 9 total items logged, got {total_items_logged}"
    print(
        f"✓ actors03 verified: Actor handle passed across distributed worker actors (total={total_items_logged})!"
    )


if __name__ == "__main__":
    verify()
