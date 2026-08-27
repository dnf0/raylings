"""Chapter 1: Ray Core Foundations - Solution 6: Multiple Returns in Remote Tasks.

Reference Solution for basics06.
"""

import ray


@ray.remote(num_returns=2)
def split_stats(numbers: list[int]) -> tuple[int, int]:
    return min(numbers), max(numbers)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    numbers = [42, 10, 99, 3, 55]

    min_ref, max_ref = split_stats.remote(numbers)
    min_val = ray.get(min_ref)
    max_val = ray.get(max_ref)

    assert min_val == 3, f"Expected min 3, got {min_val}"
    assert max_val == 99, f"Expected max 99, got {max_val}"
    print(f"✓ basics06 verified: Multiple returns unpacked into min={min_val}, max={max_val}!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
