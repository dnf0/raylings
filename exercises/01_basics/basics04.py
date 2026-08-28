"""
Exercise: exercises/01_basics/basics04.py
Topic: Passing ObjectRefs Directly to Downstream Tasks (DAG Construction)

Context & Why:
Ray allows constructing dynamic Direct Acyclic Graphs (DAGs) without pulling intermediate data
back to the driver. When you pass an `ObjectRef` directly as an argument to another `@ray.remote` task,
Ray automatically:
1. Infers the data dependency between upstream and downstream tasks.
2. Holds the downstream task in the scheduler until the upstream task completes.
3. Automatically dereferences the `ObjectRef` inside the worker before executing the downstream function.

This avoids transferring megabytes or gigabytes of intermediate data back to the driver node,
preventing memory bottlenecks and high serialization overhead.

Instructions:
1. Complete `build_pipeline(x, y)` to chain `generate_val`, `add`, and `cube` tasks.
2. Pass ObjectRefs directly between tasks without calling `ray.get()` in the pipeline builder.
3. Return the final `ObjectRef`.
"""

import ray
from ray import ObjectRef


# TODO: Define remote functions: generate_val, add, cube
def generate_val(x: int) -> int:
    return x * 3


def add(a: int, b: int) -> int:
    return a + b


def cube(x: int) -> int:
    return x**3


def build_pipeline(x: int, y: int) -> ObjectRef:
    """Build the DAG and return the final ObjectRef without calling ray.get()."""
    # TODO: Complete the pipeline by passing ObjectRefs between remote tasks
    # a_ref = generate_val.remote(x)
    # b_ref = generate_val.remote(y)
    # sum_ref = add.remote(a_ref, b_ref)
    # final_ref = cube.remote(sum_ref)
    # return final_ref
    raise NotImplementedError("Implement build_pipeline using remote tasks")


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    final_ref = build_pipeline(2, 4)
    assert isinstance(final_ref, ObjectRef), (
        f"build_pipeline must return an ObjectRef, got {type(final_ref)}"
    )

    result = ray.get(final_ref)
    expected = ((2 * 3) + (4 * 3)) ** 3  # (6 + 12)^3 = 18^3 = 5832
    assert result == expected, f"Expected {expected}, but got {result}"
    print(
        f"✓ basics04 verified: Task graph pipeline resolved to {result} without intermediate ray.get()!"
    )


if __name__ == "__main__":
    verify()
