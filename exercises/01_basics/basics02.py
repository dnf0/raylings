"""Chapter 1: Ray Core Foundations - Exercise 2: ObjectRefs and ray.get().

In Ray, calling a remote function does NOT return the computed value directly.
Instead, it immediately returns an `ObjectRef`—a lightweight identifier representing
a future value that will be computed asynchronously on a cluster worker.

Key Concepts:
1. `ObjectRef`: A 28-byte unique identifier representing an object residing in Ray's
   distributed object store.
2. `ray.get(object_ref)`: Blocks until the object is available and deserializes it.
3. Batch `ray.get([ref1, ref2, ...])`: Ray can wait on and retrieve an entire list of
   `ObjectRef`s in parallel with a single call, which is much more efficient than calling
   `ray.get()` one by one.

Your Task:
- Define a remote function `multiply(a: int, b: int) -> int`.
- Launch 5 parallel tasks calculating `i * 10` for `i` in `range(5)`.
- Store the list of `ObjectRef`s.
- Retrieve all 5 results in a single `ray.get(refs)` call.
"""

import ray
from ray import ObjectRef


# TODO: Define a remote function named `multiply` that takes two integers and returns their product.
def multiply(a: int, b: int) -> int:
    return a * b


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Launch 5 remote tasks to compute [0*10, 1*10, 2*10, 3*10, 4*10]
    # and collect their ObjectRefs in `refs`.
    refs: list[ObjectRef] = []

    # TODO: Use a single ray.get() call to retrieve all results into `results`.
    results: list[int] = []

    expected = [0, 10, 20, 30, 40]
    assert len(refs) == 5, f"Expected 5 ObjectRefs, got {len(refs)}"
    assert results == expected, f"Expected {expected}, but got {results}"
    print("✓ basics02 verified: ObjectRefs collected and fetched in batch successfully!")


if __name__ == "__main__":
    verify()
