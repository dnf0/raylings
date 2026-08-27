"""Chapter 1: Ray Core Foundations - Solution 2: ObjectRefs and ray.get().

Reference Solution for basics02.
"""

import ray
from ray import ObjectRef


@ray.remote
def multiply(a: int, b: int) -> int:
    return a * b


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    refs: list[ObjectRef] = [multiply.remote(i, 10) for i in range(5)]
    results: list[int] = ray.get(refs)

    expected = [0, 10, 20, 30, 40]
    assert len(refs) == 5, f"Expected 5 ObjectRefs, got {len(refs)}"
    assert results == expected, f"Expected {expected}, but got {results}"
    print("✓ basics02 verified: ObjectRefs collected and fetched in batch successfully!")


if __name__ == "__main__":
    verify()
