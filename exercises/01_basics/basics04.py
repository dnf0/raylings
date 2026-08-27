# I AM NOT DONE
"""Chapter 1: Ray Core Foundations - Exercise 4: Passing ObjectRefs to Tasks.

One of Ray's most powerful features is building dynamic task graphs (DAGs).
You can pass an `ObjectRef` directly as an argument to another `@ray.remote` task!

When an `ObjectRef` is passed as an argument to a remote task:
1. Ray automatically detects the task dependency.
2. The downstream task is queued until the upstream task finishes.
3. Ray passes the DE-REFERENCED value (the actual Python object) to the downstream function.
4. The driver program never needs to call `ray.get()` until it needs the final result!

Example:
    @ray.remote
    def generate(x): return x * 2

    @ray.remote
    def add(a, b): return a + b

    # No ray.get() needed between tasks!
    ref1 = generate.remote(5)
    ref2 = generate.remote(10)
    final_ref = add.remote(ref1, ref2)  # add receives (10, 20)
    result = ray.get(final_ref)         # returns 30

Your Task:
- Define three remote functions:
  1. `generate_val(x: int) -> int`: returns `x * 3`
  2. `add(a: int, b: int) -> int`: returns `a + b`
  3. `cube(x: int) -> int`: returns `x ** 3`
- Construct a task graph:
  - Generate value `a_ref` from `2` (should produce 6)
  - Generate value `b_ref` from `4` (should produce 12)
  - Pass `a_ref` and `b_ref` into `add.remote(...)` to get `sum_ref` (should produce 18)
  - Pass `sum_ref` into `cube.remote(...)` to get `final_ref` (should produce 18**3 = 5832)
- Call `ray.get()` only on `final_ref`.
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
