"""Chapter 3: Plasma Object Store & Zero-Copy - Solution 5: Handling & Resolving Nested ObjectRefs.

Reference Solution for object_store05.
"""

import ray
from ray import ObjectRef


@ray.remote
def subtask(val: int) -> int:
    return val + 100


@ray.remote
def master_task(values: list[int]) -> list[ObjectRef]:
    return [subtask.remote(v) for v in values]


def resolve_nested(outer_ref: ObjectRef) -> list[int]:
    """Resolve an ObjectRef containing a list of ObjectRefs."""
    inner_refs: list[ObjectRef] = ray.get(outer_ref)
    return ray.get(inner_refs)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    input_values = [1, 2, 3, 4, 5]

    outer_ref = master_task.remote(input_values)
    final_values = resolve_nested(outer_ref)

    expected = [101, 102, 103, 104, 105]
    assert final_values == expected, f"Expected {expected}, but got {final_values}"
    print(f"✓ object_store05 verified: Nested ObjectRefs resolved successfully ({final_values})!")


if __name__ == "__main__":
    verify()
