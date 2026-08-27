"""Chapter 1: Ray Core Foundations - Exercise 6: Multiple Returns in Remote Tasks.

By default, calling a remote function returns a single `ObjectRef`, even if that
function returns a Python tuple:

    @ray.remote
    def func():
        return 1, 2

    ref = func.remote()          # Returns a SINGLE ObjectRef representing (1, 2)
    val1, val2 = ray.get(ref)    # Must get the whole tuple at once

If you want the remote function to return multiple distinct `ObjectRef`s, configure
`num_returns=N` in the `@ray.remote` decorator:

    @ray.remote(num_returns=2)
    def func():
        return 1, 2

    ref1, ref2 = func.remote()   # Returns TWO separate ObjectRefs!
    val1 = ray.get(ref1)         # Can get or pass ref1 independently
    val2 = ray.get(ref2)         # Can get or pass ref2 independently

Key Benefits:
1. Downstream tasks can depend on just `ref1` without blocking on `ref2`.
2. Enables clean decomposition of pipeline stages (e.g. splitting datasets into features and labels).

Your Task:
- Define `@ray.remote(num_returns=2) def split_stats(numbers: list[int]) -> tuple[int, int]`
  that returns the minimum and maximum of the given list.
- Call `split_stats.remote([42, 10, 99, 3, 55])` and unpack the two `ObjectRef`s.
- Retrieve and verify min and max separately using `ray.get()`.
"""

# I AM NOT DONE
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
