"""
Exercise: exercises/04_scheduling_resources/scheduling03.py
Topic: Placement Groups: STRICT_SPREAD Strategy

Context & Why:
Placement groups allow reserving compute bundles atomically across cluster nodes.
The `STRICT_SPREAD` strategy guarantees that each bundle in the placement group is placed
on a **completely distinct physical node**.

This is crucial for high-availability services and fault-tolerant replicated systems where no two
worker replicas should share the same fault domain.

Instructions:
1. Create a placement group with `strategy="STRICT_SPREAD"`.
2. Schedule worker actors across the placement group bundles.
"""

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
