"""Chapter 7: Production Patterns & Anti-Patterns - Solution 1: Fixing ray.get() Inside Tasks.

Reference Solution for antipattern01.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray


@ray.remote
def stage1() -> int:
    return 42


@ray.remote
def stage2(val: int) -> int:
    return val + 100


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    ref1 = stage1.remote()
    ref2 = stage2.remote(ref1)
    result = ray.get(ref2)

    assert result == 142, f"Expected 142, got {result}"
    print(
        f"✓ antipattern01 verified: ObjectRef pipelined cleanly without blocking ray.get() inside tasks ({result})!"
    )


if __name__ == "__main__":
    verify()
