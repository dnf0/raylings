"""
Exercise: exercises/07_patterns_and_antipatterns/antipattern03.py
Topic: Actor Bottleneck Elimination via Sharding

Context & Why:
Because a single Ray actor executes method calls sequentially, routing high-throughput traffic
from 100 workers to a single centralized actor creates a severe serialization bottleneck.

Sharding the actor state across an Actor Pool or partitioning keys across multiple independent actors
allows concurrent reads and writes, achieving horizontal scalability.

Instructions:
1. Partition workloads across a pool of shard actors instead of a single bottleneck actor.
2. Verify throughput gains.
"""

# I AM NOT DONE

import ray
from ray.util.actor_pool import ActorPool


# TODO: Define StatelessWorker actor class
class StatelessWorker:
    def compute(self, x: int) -> int:
        return x * 10


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [1, 2, 3, 4, 5, 6, 7, 8]

    # TODO: Instantiate 4 worker actors and wrap in ActorPool
    # workers = [StatelessWorker.remote() for _ in range(4)]
    # pool = ActorPool(workers)

    # TODO: Map compute across pool
    # results = list(pool.map(lambda a, v: a.compute.remote(v), items))
    results = []

    expected = [x * 10 for x in items]
    assert results == expected, f"Expected {expected}, got {results}"
    print(
        f"✓ antipattern03 verified: ActorPool distributed requests across 4 actors successfully ({results})!"
    )


if __name__ == "__main__":
    verify()
