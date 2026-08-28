"""
Exercise: exercises/07_patterns_and_antipatterns/antipattern04.py
Topic: Tree-Structured Distributed Aggregation

Context & Why:
Aggregating $N$ items on a single driver process with `sum(ray.get(refs))` requires transferring all
$N$ results back to the driver's memory, creating an $O(N)$ network and memory bottleneck.

A **Tree Aggregate** recursively pairs and reduces intermediate results across distributed workers in
log_k(N) steps. The driver only ever receives the single final scalar result.

Instructions:
1. Implement a recursive tree reduction using `@ray.remote` aggregator tasks.
2. Verify O(log N) aggregation depth.
"""

# I AM NOT DONE

import ray


# TODO: Define add_pair remote task
def add_pair(a: int, b: int) -> int:
    return a + b


# TODO: Define produce_leaf remote task
def produce_leaf(val: int) -> int:
    return val


# TODO: Implement tree_reduce
def tree_reduce(refs: list[ray.ObjectRef]) -> ray.ObjectRef:
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
