"""
Exercise: exercises/04_scheduling_resources/scheduling05.py
Topic: Gang Scheduling with Multi-Bundle Placement Groups

Context & Why:
Distributed training algorithms (e.g. PyTorch DDP, Ring All-Reduce) require all $N$ workers to be
ready simultaneously before training begins. If only $N-1$ workers are scheduled, the job deadlocks.

Ray's placement groups provide **gang scheduling**: `ray.util.placement_group(...)` waits until ALL
bundles can be reserved atomically before allowing any worker to start, preventing resource deadlock.

Instructions:
1. Define a multi-bundle placement group and wait for readiness using `pg.ready()`.
2. Schedule gang workers into the reserved bundles.
"""

import ray
from ray.util.placement_group import (
    placement_group,
    placement_group_table,
    remove_placement_group,
)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Create a 3-bundle placement group of {"CPU": 0.25} with strategy="PACK"
    # pg = placement_group([{"CPU": 0.25}] * 3, strategy="PACK")
    # ray.get(pg.ready())
    pg = None

    # TODO: Inspect placement group state
    # table = placement_group_table(pg)
    # state = table["state"]
    # bundles_count = len(table["bundles"])
    # remove_placement_group(pg)
    state, bundles_count = None, None

    assert pg is not None
    assert state == "CREATED", f"Expected pg state 'CREATED', got {state}"
    assert bundles_count == 3, f"Expected 3 bundles, got {bundles_count}"
    print(
        f"✓ scheduling05 verified: Gang-scheduled placement group lifecycle verified (state={state}, bundles={bundles_count})!"
    )


if __name__ == "__main__":
    verify()
