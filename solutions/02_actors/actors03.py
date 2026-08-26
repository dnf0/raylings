"""Chapter 2: Distributed State & Actors - Solution 3: Passing Actor Handles.

Reference Solution for actors03.
"""

import ray
from ray.actor import ActorHandle


@ray.remote
class MetricsLogger:
    def __init__(self) -> None:
        self.records: dict[str, int] = {}

    def log(self, worker_id: str, count: int) -> None:
        self.records[worker_id] = self.records.get(worker_id, 0) + count

    def get_total(self) -> int:
        return sum(self.records.values())


@ray.remote
class BatchWorker:
    def __init__(self, worker_id: str, logger: ActorHandle) -> None:
        self.worker_id = worker_id
        self.logger = logger

    def process(self, items: list[int]) -> int:
        total = sum(items)
        ray.get(self.logger.log.remote(self.worker_id, len(items)))
        return total


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    logger = MetricsLogger.remote()

    batches = [
        ("worker_1", [1, 2, 3]),
        ("worker_2", [4, 5]),
        ("worker_3", [6, 7, 8, 9]),
    ]
    workers = [BatchWorker.remote(wid, logger) for wid, _ in batches]
    task_refs = [w.process.remote(items) for w, (_, items) in zip(workers, batches, strict=False)]
    batch_sums = ray.get(task_refs)
    total_items_logged = ray.get(logger.get_total.remote())

    assert batch_sums == [6, 9, 30], f"Expected batch sums [6, 9, 30], got {batch_sums}"
    assert total_items_logged == 9, f"Expected 9 total items logged, got {total_items_logged}"
    print(f"✓ actors03 verified: Actor handle passed across distributed worker actors (total={total_items_logged})!")


if __name__ == "__main__":
    verify()
