"""Chapter 13: Observability - Exercise 2: Diagnosing Object Store Memory.

Ray's shared-memory object store (Plasma) holds immutable distributed objects.
Understanding ObjectRef lifecycle and memory pinning prevents distributed memory leaks.

Key Concepts:
- `ray.util.state.list_objects()`: Returns metadata on all objects in the cluster store.
- When an ObjectRef goes out of scope (or is explicitly deleted via `del ref`),
  its Plasma memory becomes eligible for garbage collection.

Your Task:
- In `allocate_and_inspect_objects() -> int`:
  - Put a large payload `ray.put([0] * 100_000)` into the object store.
  - Query `objects = ray.util.state.list_objects()`.
  - Count objects with `data_size > 50_000`.
  - Return the count.
- In `verify()`:
  - Assert that at least 1 large object is detected in the object store.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray.util.state import list_objects


def allocate_and_inspect_objects() -> int:
    # TODO: Put object into store, query list_objects, and count large objects
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)
    try:
        count = allocate_and_inspect_objects()
        assert count >= 1, f"Expected at least 1 large object in store, found {count}"
        print(
            f"✓ perf02 verified: Object store memory inspector identified {count} active objects!"
        )
    finally:
        ray.shutdown()


if __name__ == "__main__":
    verify()
