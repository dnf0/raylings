"""
Exercise: exercises/02_actors/actors03.py
Topic: Passing Actor Handles for Distributed Coordination

Context & Why:
In Ray, `ActorHandle`s are first-class serializable objects that can be passed as arguments
to other remote tasks and actors. Any worker receiving an `ActorHandle` can invoke remote methods
on that shared actor instance.

This pattern is widely used in distributed machine learning for centralized parameter servers,
global metric aggregators, distributed barrier synchronization, and progress tracking.

Instructions:
1. Define a `MetricTracker` actor that aggregates counts from multiple worker tasks.
2. Pass the `MetricTracker` handle into multiple concurrent `@ray.remote` tasks.
3. Verify that all workers successfully reported their progress to the single actor.
"""

# I AM NOT DONE

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
