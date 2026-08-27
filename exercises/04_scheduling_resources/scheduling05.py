"""Chapter 4: Scheduling & Resources - Exercise 5: Gang Scheduling & Multi-Bundle Lifecycle.

Gang Scheduling is the practice of scheduling all related distributed processes simultaneously
to avoid deadlocks (where worker A holds resource 1 waiting for worker B, while worker B holds
resource 2 waiting for worker A).

Ray Placement Groups guarantee atomic gang allocation:
1. Creation: `pg = placement_group(bundles, strategy=...)`
2. Readiness Barrier: `ray.get(pg.ready())` blocks until ALL bundles are allocated.
3. Introspection: `placement_group_table(pg)` returns metadata and state (`"CREATED"`).
4. Teardown: `remove_placement_group(pg)` frees up cluster resources.

Your Task:
- In `verify()`:
  - Create a placement group with 3 bundles of `{"CPU": 0.25}` using `strategy="PACK"`.
  - Wait for the placement group to be ready.
  - Query the placement group table with `placement_group_table(pg)` and assert `state == "CREATED"`.
  - Clean up the placement group using `remove_placement_group(pg)`.
"""

# I AM NOT DONE
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
