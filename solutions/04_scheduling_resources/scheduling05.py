"""Chapter 4: Scheduling & Resources - Solution 5: Gang Scheduling & Multi-Bundle Lifecycle.

Reference Solution for scheduling05.
"""

import ray
from ray.util.placement_group import (
    placement_group,
    placement_group_table,
    remove_placement_group,
)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    pg = placement_group([{"CPU": 0.25}] * 3, strategy="PACK")
    ray.get(pg.ready())

    table = placement_group_table(pg)
    state = table["state"]
    bundles_count = len(table["bundles"])
    remove_placement_group(pg)

    assert pg is not None
    assert state == "CREATED", f"Expected pg state 'CREATED', got {state}"
    assert bundles_count == 3, f"Expected 3 bundles, got {bundles_count}"
    print(
        f"✓ scheduling05 verified: Gang-scheduled placement group lifecycle verified (state={state}, bundles={bundles_count})!"
    )


if __name__ == "__main__":
    verify()
