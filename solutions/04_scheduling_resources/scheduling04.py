"""Chapter 4: Scheduling & Resources - Solution 4: Placement Groups & PACK Strategy.

Reference Solution for scheduling04.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray.util.placement_group import placement_group
from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy


@ray.remote(num_cpus=0.5)
class ColocatedWorker:
    def __init__(self, name: str) -> None:
        self.name = name
        self.node_id = ray.get_runtime_context().get_node_id()

    def get_info(self) -> tuple[str, str]:
        return self.name, self.node_id


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    pg = placement_group([{"CPU": 0.5}, {"CPU": 0.5}], strategy="PACK")
    ray.get(pg.ready())

    strat0 = PlacementGroupSchedulingStrategy(placement_group=pg, placement_group_bundle_index=0)
    strat1 = PlacementGroupSchedulingStrategy(placement_group=pg, placement_group_bundle_index=1)
    worker1 = ColocatedWorker.options(scheduling_strategy=strat0).remote("worker_1")
    worker2 = ColocatedWorker.options(scheduling_strategy=strat1).remote("worker_2")
    info1 = ray.get(worker1.get_info.remote())
    info2 = ray.get(worker2.get_info.remote())

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
