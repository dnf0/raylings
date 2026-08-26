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
def process_batch(logger: ActorHandle, worker_id: str, items: list[int]) -> int:
    total = sum(items)
    logger.log.remote(worker_id, len(items))
    return total


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    logger = MetricsLogger.remote()

    batches = [
        ("worker_1", [1, 2, 3]),
        ("worker_2", [4, 5]),
        ("worker_3", [6, 7, 8, 9]),
    ]
    task_refs = [process_batch.remote(logger, wid, items) for wid, items in batches]
    batch_sums = ray.get(task_refs)
    total_items_logged = ray.get(logger.get_total.remote())

    assert batch_sums == [6, 9, 30], f"Expected batch sums [6, 9, 30], got {batch_sums}"
    assert total_items_logged == 9, f"Expected 9 total items logged, got {total_items_logged}"
    print(f"✓ actors03 verified: Actor handle passed across distributed worker tasks (total={total_items_logged})!")


if __name__ == "__main__":
    verify()
