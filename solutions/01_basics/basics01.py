"""Chapter 1: Ray Core Foundations - Solution 1: Ray Init & First Remote Task.

Reference Solution for basics01.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray


@ray.remote
def square(x: int) -> int:
    return x * x


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    result_ref = square.remote(7)
    result = ray.get(result_ref)

    assert ray.is_initialized(), "Ray should be initialized"
    assert result == 49, f"Expected 49, but got {result}"
    print("✓ basics01 verified: Ray initialized and remote task executed successfully!")


if __name__ == "__main__":
    verify()
