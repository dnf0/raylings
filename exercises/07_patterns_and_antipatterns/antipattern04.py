# I AM NOT DONE
"""Chapter 7: Production Patterns & Anti-Patterns - Exercise 4: Tree-Structured Reduction (Tree-Reduce).

Anti-Pattern: Linear Accumulation on the Driver.
If you have 1,024 distributed partial results and call `ray.get()` on all 1,024 refs to sum
them sequentially in Python on the driver, you create an O(N) memory and bandwidth bottleneck
on the driver node.

Correct Pattern: Tree-Structured Reduction (Tree-Reduce).
Combine pairs of results in parallel across the cluster using a binary tree reduction DAG!
This reduces driver communication to 1 single object and parallelizes aggregation depth to O(log2 N).

```python
@ray.remote
def add_pair(a: int, b: int) -> int:
    return a + b

# Tree-reduce loop:
refs = [produce_partial.remote(i) for i in range(16)]
while len(refs) > 1:
    next_refs = []
    for i in range(0, len(refs), 2):
        if i + 1 < len(refs):
            next_refs.append(add_pair.remote(refs[i], refs[i + 1]))
        else:
            next_refs.append(refs[i])
    refs = next_refs
total = ray.get(refs[0])
```

Your Task:
- Define `@ray.remote` task `add_pair(a: int, b: int) -> int`: returns `a + b`.
- Define `@ray.remote` task `produce_leaf(val: int) -> int`: returns `val`.
- Implement a function `tree_reduce(refs: list[ray.ObjectRef]) -> ray.ObjectRef`:
  - Reduces the list of `ObjectRef`s in pairs until a single root `ObjectRef` remains.
- In `verify()`:
  - Create 8 leaf refs for values `[1, 2, 3, 4, 5, 6, 7, 8]` using `produce_leaf.remote(x)`.
  - Pass the leaf refs into `tree_reduce`.
  - Assert the resolved sum is `36`.
"""

import ray


# TODO: Define add_pair remote task
def add_pair(a: int, b: int) -> int:
    return a + b


# TODO: Define produce_leaf remote task
def produce_leaf(val: int) -> int:
    return val


# TODO: Implement tree_reduce
def tree_reduce(refs: list) -> ray.ObjectRef:
    # current = list(refs)
    # while len(current) > 1:
    #     next_level = []
    #     for i in range(0, len(current), 2):
    #         if i + 1 < len(current):
    #             next_level.append(add_pair.remote(current[i], current[i + 1]))
    #         else:
    #             next_level.append(current[i])
    #     current = next_level
    # return current[0]
    return refs[0] if refs else None


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    values = [1, 2, 3, 4, 5, 6, 7, 8]
    # TODO: Create leaf refs and perform tree_reduce
    # leaf_refs = [produce_leaf.remote(v) for v in values]
    # root_ref = tree_reduce(leaf_refs)
    # total = ray.get(root_ref)
    total = None

    assert total == 36, f"Expected total 36 (sum of 1..8), got {total}"
    print(
        f"✓ antipattern04 verified: Tree-reduction computed 8 leaf nodes in O(log2 N) depth (total={total})!"
    )


if __name__ == "__main__":
    verify()
