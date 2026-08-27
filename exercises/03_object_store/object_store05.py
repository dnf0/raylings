"""Chapter 3: Plasma Object Store & Zero-Copy - Exercise 5: Handling & Resolving Nested ObjectRefs.

A subtle nuance in distributed programming with Ray occurs when tasks return other `ObjectRef`s,
or when `ObjectRef`s are placed inside data structures (lists, dictionaries, dataclasses).

Nested ObjectRefs:
If remote task `A` invokes remote task `B` and returns `B`'s `ObjectRef`:

    @ray.remote
    def inner_task(x):
        return x * 10

    @ray.remote
    def outer_task(x):
        return inner_task.remote(x)  # Returns an ObjectRef!

    ref = outer_task.remote(5)       # ref is an ObjectRef[ObjectRef[int]]
    nested_ref = ray.get(ref)        # First get() returns the inner ObjectRef
    final_val = ray.get(nested_ref)  # Second get() returns the actual value (50)

Key Rules:
1. `ray.get(ObjectRef[ObjectRef[T]])` yields `ObjectRef[T]`.
2. When a task receives a dictionary containing `ObjectRef`s (`{"key": ref}`), Ray does NOT
   automatically dereference refs nested inside containers—the task receives the `ObjectRef`
   and must call `ray.get()` on it if needed.

Your Task:
- Define `@ray.remote def subtask(val: int) -> int` that returns `val + 100`.
- Define `@ray.remote def master_task(values: list[int]) -> list[ObjectRef]` that launches
  a `subtask.remote(v)` for each value and returns the list of `ObjectRef`s.
- Write a helper `resolve_nested(outer_ref: ObjectRef) -> list[int]` that resolves both the
  outer list and all nested inner `ObjectRef`s into a plain list of integers.
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
