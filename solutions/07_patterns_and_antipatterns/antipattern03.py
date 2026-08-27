"""Chapter 7: Production Patterns & Anti-Patterns - Solution 3: Fixing Actor Bottlenecks.

Reference Solution for antipattern03.
"""

import ray
from ray.util.actor_pool import ActorPool


@ray.remote
class StatelessWorker:
    def compute(self, x: int) -> int:
        return x * 10


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [1, 2, 3, 4, 5, 6, 7, 8]

    workers = [StatelessWorker.remote() for _ in range(4)]
    pool = ActorPool(workers)

    results = list(pool.map(lambda a, v: a.compute.remote(v), items))

    expected = [x * 10 for x in items]
    assert results == expected, f"Expected {expected}, got {results}"
    print(
        f"✓ antipattern03 verified: ActorPool distributed requests across 4 actors successfully ({results})!"
    )


if __name__ == "__main__":
    verify()
