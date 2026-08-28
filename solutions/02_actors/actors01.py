"""Chapter 2: Distributed State & Actors - Solution 1: Stateful Actor Lifecycle.

Reference Solution for actors01.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray


@ray.remote
class Counter:
    def __init__(self, initial_value: int = 0) -> None:
        self.count = initial_value

    def increment(self, step: int = 1) -> int:
        self.count += step
        return self.count

    def decrement(self, step: int = 1) -> int:
        self.count -= step
        return self.count

    def get_count(self) -> int:
        return self.count


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    counter = Counter.remote(initial_value=10)
    counter.increment.remote(5)
    counter.decrement.remote(3)
    final_count = ray.get(counter.get_count.remote())

    assert final_count == 12, f"Expected final count 12, got {final_count}"
    print(
        f"✓ actors01 verified: Stateful Actor lifecycle and operations confirmed (count={final_count})!"
    )


if __name__ == "__main__":
    verify()
