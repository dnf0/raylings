"""Chapter 4: Scheduling & Resources - Exercise 3: Placement Groups & SPREAD Strategy.

Placement Groups allow you to atomically reserve groups of resource bundles across a cluster.
They are essential for:
1. Gang Scheduling: Guaranteeing all necessary workers can be scheduled together before starting.
2. Topology Control: Packing tasks together for low-latency communication (PACK) or spreading
   them out across failure domains / nodes (SPREAD).

Placement Group Strategies:
- `STRICT_SPREAD`: Each bundle MUST be placed on a separate node (fails if not enough nodes).
- `SPREAD`: Ray places bundles on different nodes on a best-effort basis.
- `STRICT_PACK`: All bundles MUST be placed on the exact same single node.
- `PACK`: Ray tries to pack bundles on as few nodes as possible.

To schedule a task or actor into a placement group:
```python
from ray.util.placement_group import placement_group
from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy

# Create placement group with 2 CPU bundles
pg = placement_group([{"CPU": 1}, {"CPU": 1}], strategy="SPREAD")
ray.get(pg.ready())  # Block until resources are reserved

# Schedule task into bundle 0
strategy = PlacementGroupSchedulingStrategy(placement_group=pg, placement_group_bundle_index=0)
ref = my_task.options(scheduling_strategy=strategy).remote()
```

Your Task:
- Define a `@ray.remote(num_cpus=0.5)` function `spread_worker(worker_id: int) -> dict[str, int]`
  that returns `{"worker_id": worker_id, "status": 1}`.
- In `verify()`, create a placement group with 2 bundles of `{"CPU": 0.5}` each using `strategy="SPREAD"`.
- Wait for the placement group to be ready using `ray.get(pg.ready())`.
- Schedule 2 `spread_worker` tasks into bundle 0 and bundle 1 respectively.
- Collect and verify the results.
"""

# I AM NOT DONE
import ray
from ray.util.placement_group import placement_group
from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy


# TODO: Define spread_worker remote task
def spread_worker(worker_id: int) -> dict[str, int]:
    return {}


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Create a placement group with 2 bundles of {"CPU": 0.5} and strategy="SPREAD"
    # pg = placement_group([{"CPU": 0.5}, {"CPU": 0.5}], strategy="SPREAD")
    # ray.get(pg.ready())

    # TODO: Schedule spread_worker(0) into bundle 0 and spread_worker(1) into bundle 1
    # strat0 = PlacementGroupSchedulingStrategy(placement_group=pg, placement_group_bundle_index=0)
    # strat1 = PlacementGroupSchedulingStrategy(placement_group=pg, placement_group_bundle_index=1)
    # ref0 = spread_worker.options(scheduling_strategy=strat0).remote(0)
    # ref1 = spread_worker.options(scheduling_strategy=strat1).remote(1)
    # results = ray.get([ref0, ref1])
    results = None

    assert results == [
        {"worker_id": 0, "status": 1},
        {"worker_id": 1, "status": 1},
    ], f"Expected results, got {results}"
    print(
        f"✓ scheduling03 verified: Placement group created and bundles scheduled successfully ({results})!"
    )


if __name__ == "__main__":
    verify()
