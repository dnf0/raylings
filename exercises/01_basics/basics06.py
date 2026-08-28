"""
Exercise: exercises/01_basics/basics06.py
Topic: Multiple Return Values in Remote Tasks (num_returns)

Context & Why:
By default, `@ray.remote` functions return a single `ObjectRef`, even if the Python function
returns a tuple. When downstream tasks only need a subset of the returned data, returning a single
tuple forces all downstream tasks to depend on the entire tuple.

Configuring `@ray.remote(num_returns=N)` instructs Ray to partition the return values into `N`
distinct, independent `ObjectRef`s. Downstream tasks can subscribe to specific return elements,
enabling finer-grained dependency graphs and avoiding unnecessary data transfers.

Instructions:
1. Configure `split_stats` with `@ray.remote(num_returns=2)`.
2. Unpack the two returned ObjectRefs: `min_ref, max_ref = split_stats.remote(numbers)`.
3. Retrieve and verify both values independently.
"""

import ray


# TODO: Decorate split_stats with @ray.remote(num_returns=2)
def split_stats(numbers: list[int]) -> tuple[int, int]:
    return min(numbers), max(numbers)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    numbers = [42, 10, 99, 3, 55]
    _ = numbers

    # TODO: Call split_stats.remote(numbers) and unpack the returned ObjectRefs
    # min_ref, max_ref = split_stats.remote(numbers)
    # min_val = ray.get(min_ref)
    # max_val = ray.get(max_ref)
    min_val, max_val = None, None

    assert min_val == 3, f"Expected min 3, got {min_val}"
    assert max_val == 99, f"Expected max 99, got {max_val}"
    print(f"✓ basics06 verified: Multiple returns unpacked into min={min_val}, max={max_val}!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
