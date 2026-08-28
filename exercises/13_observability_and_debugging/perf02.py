"""
Exercise: exercises/13_observability_and_debugging/perf02.py
Topic: Diagnosing Memory Leaks with ray memory

Context & Why:
Holding onto `ObjectRef`s in global Python variables or long-lived actor state prevents Plasma from
garbage-collecting the underlying shared memory buffers.
`ray.util.state.list_objects()` or `ray.experimental.internal_kv` APIs inspect active object references,
pinned memory allocations, and spilled bytes across nodes.

Instructions:
1. Identify and release leaked ObjectRefs.
2. Verify memory reclamation in the object store.
"""

# I AM NOT DONE

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
