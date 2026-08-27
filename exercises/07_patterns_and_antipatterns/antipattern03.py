"""Chapter 7: Production Patterns & Anti-Patterns - Exercise 3: Fixing Actor Bottlenecks.

Anti-Pattern: The Single Monolithic Actor Bottleneck.
By default, Ray actors execute method invocations sequentially on a single thread.
If 100 client tasks all call methods on a single actor instance, all 100 requests queue up
behind each other in FIFO order, creating a severe serial bottleneck regardless of cluster size.

Correct Pattern: Actor Pools / Sharding.
When workloads are stateless or partitionable, instantiate a pool of N worker actors
and use `ray.util.ActorPool` or round-robin dispatching to distribute concurrent requests
evenly across the pool:

```python
from ray.util.actor_pool import ActorPool

workers = [WorkerActor.remote() for _ in range(4)]
pool = ActorPool(workers)

# Parallel map across the actor pool
results = list(pool.map(lambda a, v: a.process.remote(v), items))
```

Your Task:
- Define a `@ray.remote` actor class `StatelessWorker`:
  - Method `compute(self, x: int) -> int`: returns `x * 10`.
- In `verify()`:
  - Create a list of 4 `StatelessWorker` actors.
  - Create an `ActorPool(workers)`.
  - Use `pool.map(lambda a, v: a.compute.remote(v), [1, 2, 3, 4, 5, 6, 7, 8])` to process all 8 values.
  - Collect the mapped results as a list and assert it equals `[10, 20, 30, 40, 50, 60, 70, 80]`.
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
