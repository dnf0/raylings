"""Chapter 4: Scheduling & Resources - Exercise 4: Placement Groups & PACK Strategy.

When building latency-critical distributed systems (such as high-speed actor pipelines or
local shared-memory training workers), you often want tasks/actors co-located on the
SAME physical node to maximize zero-copy shared memory performance.

The `PACK` (or `STRICT_PACK`) strategy places all requested resource bundles on the
same node:
```python
pg = placement_group([{"CPU": 0.5}, {"CPU": 0.5}], strategy="PACK")
ray.get(pg.ready())
```

Your Task:
- Define a `@ray.remote(num_cpus=0.5)` actor `ColocatedWorker` with:
  - `__init__(self, name: str)`: stores `self.name = name` and `self.node_id = ray.get_runtime_context().get_node_id()`
  - `get_info(self) -> tuple[str, str]`: returns `(self.name, self.node_id)`
- In `verify()`, create a placement group with 2 bundles of `{"CPU": 0.5}` using `strategy="PACK"`.
- Wait for the placement group to be ready.
- Instantiate 2 `ColocatedWorker` actors into bundle 0 and bundle 1 of the placement group.
- Retrieve their info and verify that both actors were scheduled on the exact SAME node ID.
"""

# I AM NOT DONE
import ray
from ray.util.placement_group import placement_group
from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy


# TODO: Define ColocatedWorker actor
class ColocatedWorker:
    def __init__(self, name: str) -> None:
        self.name = name
        self.node_id = ray.get_runtime_context().get_node_id()

    def get_info(self) -> tuple[str, str]:
        return self.name, self.node_id


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Create a placement group with 2 bundles of {"CPU": 0.5} and strategy="PACK"
    # pg = placement_group([{"CPU": 0.5}, {"CPU": 0.5}], strategy="PACK")
    # ray.get(pg.ready())

    # TODO: Instantiate two ColocatedWorker actors in bundle 0 and bundle 1
    # strat0 = PlacementGroupSchedulingStrategy(placement_group=pg, placement_group_bundle_index=0)
    # strat1 = PlacementGroupSchedulingStrategy(placement_group=pg, placement_group_bundle_index=1)
    # worker1 = ColocatedWorker.options(scheduling_strategy=strat0).remote("worker_1")
    # worker2 = ColocatedWorker.options(scheduling_strategy=strat1).remote("worker_2")
    # info1 = ray.get(worker1.get_info.remote())
    # info2 = ray.get(worker2.get_info.remote())
    info1, info2 = None, None

    assert info1 is not None and info2 is not None
    assert info1[0] == "worker_1" and info2[0] == "worker_2"
    assert info1[1] == info2[1], (
        f"Expected identical node IDs for packed actors, got {info1[1]} vs {info2[1]}"
    )
    print(
        f"✓ scheduling04 verified: Both actors colocated on node {info1[1]} via PACK placement group!"
    )


if __name__ == "__main__":
    verify()
