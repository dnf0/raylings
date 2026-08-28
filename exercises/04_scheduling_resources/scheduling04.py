"""
Exercise: exercises/04_scheduling_resources/scheduling04.py
Topic: Placement Groups: STRICT_PACK Strategy

Context & Why:
Conversely, the `STRICT_PACK` strategy guarantees that all bundles in the placement group are
co-located on the **same physical node**.

This minimizes network latency and maximizes shared-memory Plasma throughput for tightly-coupled
collaborative tasks (e.g. multi-GPU model parallel forward passes).

Instructions:
1. Create a placement group with `strategy="STRICT_PACK"`.
2. Schedule actors into the co-located bundles.
"""

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
