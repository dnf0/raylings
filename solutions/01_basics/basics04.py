"""Chapter 1: Ray Core Foundations - Solution 4: Passing ObjectRefs to Tasks.

Reference Solution for basics04.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import ObjectRef


@ray.remote
def generate_val(x: int) -> int:
    return x * 3


@ray.remote
def add(a: int, b: int) -> int:
    return a + b


@ray.remote
def cube(x: int) -> int:
    return x**3


def build_pipeline(x: int, y: int) -> ObjectRef:
    """Build the DAG and return the final ObjectRef without calling ray.get()."""
    a_ref = generate_val.remote(x)
    b_ref = generate_val.remote(y)
    sum_ref = add.remote(a_ref, b_ref)
    final_ref = cube.remote(sum_ref)
    return final_ref


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
