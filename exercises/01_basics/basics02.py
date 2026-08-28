"""
Exercise: exercises/01_basics/basics02.py
Topic: ObjectRefs and ray.get() Batch Retrieval

Context & Why:
In Ray, calling a remote function does NOT return the computed value directly.
Instead, it immediately returns an `ObjectRef`—a lightweight 28-byte unique identifier
representing a future value stored in Ray's distributed Plasma object store.

Calling `ray.get(ref)` sequentially in a loop blocks the driver on each individual task,
defeating parallelism. Instead, Ray allows passing a list of ObjectRefs to `ray.get([ref1, ref2, ...])`.
This batch retrieval instructs the Ray core worker to wait for all objects in parallel and
deserialize them efficiently in a single operation.

Instructions:
1. Decorate `multiply` with `@ray.remote`.
2. Launch 5 parallel tasks calculating `i * 10` for `i` in `range(5)` using list comprehension.
3. Collect the `ObjectRef`s in a list.
4. Retrieve all 5 results in parallel with a single `ray.get(refs)` call.
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
