"""
Exercise: exercises/03_object_store/object_store05.py
Topic: Resolving Nested ObjectRefs

Context & Why:
When a remote task returns another `ObjectRef` (e.g. dynamic task spawning), Ray creates a nested
future: `ObjectRef[ObjectRef[T]]`.

Calling `ray.get()` once only unpacks the outer reference, returning an inner `ObjectRef`.
To obtain the final value, Ray provides automatic dereferencing or double-get patterns.

Instructions:
1. Implement nested task execution.
2. Unpack nested `ObjectRef`s to retrieve the underlying payload.
"""

# I AM NOT DONE

import ray
from ray import ObjectRef


# TODO: Define subtask remote function
def subtask(val: int) -> int:
    return val + 100


# TODO: Define master_task remote function returning list of ObjectRefs
def master_task(values: list[int]) -> list[ObjectRef]:
    # return [subtask.remote(v) for v in values]
    pass


def resolve_nested(outer_ref: ObjectRef) -> list[int]:
    """Resolve an ObjectRef containing a list of ObjectRefs."""
    # TODO: 1. Call ray.get(outer_ref) to get the list of inner ObjectRefs
    # TODO: 2. Call ray.get() on the list of inner ObjectRefs to get final integers
    # inner_refs = ray.get(outer_ref)
    # return ray.get(inner_refs)
    return []


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    input_values = [1, 2, 3, 4, 5]
    _ = input_values

    # TODO: Launch master_task.remote(input_values)
    # outer_ref = master_task.remote(input_values)
    # final_values = resolve_nested(outer_ref)
    final_values: list[int] = []

    expected = [101, 102, 103, 104, 105]
    assert final_values == expected, f"Expected {expected}, but got {final_values}"
    print(f"✓ object_store05 verified: Nested ObjectRefs resolved successfully ({final_values})!")


if __name__ == "__main__":
    verify()
