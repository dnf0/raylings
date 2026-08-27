"""Chapter 13: Observability - Solution 2: Diagnosing Object Store Memory.

Reference Solution for perf02.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray.util.state import list_objects


def allocate_and_inspect_objects() -> int:
    ref = ray.put([0] * 100_000)
    objects = list_objects()
    large_objects = [
        obj
        for obj in objects
        if (getattr(obj, "object_size", 0) or getattr(obj, "data_size", 0)) > 50_000
    ]
    # Keep ref in scope until inspection completes
    _ = ray.get(ref)
    return len(large_objects)


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
