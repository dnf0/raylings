"""Chapter 4: Scheduling & Resources - Solution 3: Placement Groups & SPREAD Strategy.

Reference Solution for scheduling03.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray.util.placement_group import placement_group
from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy


@ray.remote(num_cpus=0.5)
def spread_worker(worker_id: int) -> dict[str, int]:
    return {"worker_id": worker_id, "status": 1}


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    pg = placement_group([{"CPU": 0.5}, {"CPU": 0.5}], strategy="SPREAD")
    ray.get(pg.ready())

    strat0 = PlacementGroupSchedulingStrategy(placement_group=pg, placement_group_bundle_index=0)
    strat1 = PlacementGroupSchedulingStrategy(placement_group=pg, placement_group_bundle_index=1)
    ref0 = spread_worker.options(scheduling_strategy=strat0).remote(0)
    ref1 = spread_worker.options(scheduling_strategy=strat1).remote(1)
    results = ray.get([ref0, ref1])

    assert results == [
        {"worker_id": 0, "status": 1},
        {"worker_id": 1, "status": 1},
    ], f"Expected results, got {results}"
    print(
        f"✓ scheduling03 verified: Placement group created and bundles scheduled successfully ({results})!"
    )


if __name__ == "__main__":
    verify()
