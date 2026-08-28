"""Chapter 7: Production Patterns & Anti-Patterns - Solution 4: Tree-Structured Reduction (Tree-Reduce).

Reference Solution for antipattern04.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray


@ray.remote
def add_pair(a: int, b: int) -> int:
    return a + b


@ray.remote
def produce_leaf(val: int) -> int:
    return val


def tree_reduce(refs: list[ray.ObjectRef]) -> ray.ObjectRef:
    current = list(refs)
    while len(current) > 1:
        next_level = []
        for i in range(0, len(current), 2):
            if i + 1 < len(current):
                next_level.append(add_pair.remote(current[i], current[i + 1]))
            else:
                next_level.append(current[i])
        current = next_level
    return current[0]


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    values = [1, 2, 3, 4, 5, 6, 7, 8]
    leaf_refs = [produce_leaf.remote(v) for v in values]
    root_ref = tree_reduce(leaf_refs)
    total = ray.get(root_ref)

    assert total == 36, f"Expected total 36 (sum of 1..8), got {total}"
    print(
        f"✓ antipattern04 verified: Tree-reduction computed 8 leaf nodes in O(log2 N) depth (total={total})!"
    )


if __name__ == "__main__":
    verify()
