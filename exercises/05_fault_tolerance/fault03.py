"""
Exercise: exercises/05_fault_tolerance/fault03.py
Topic: Lineage Reconstruction of Lost Objects

Context & Why:
If a cluster node fails and its Plasma object store memory is destroyed, Ray does not necessarily
fail the entire job. Ray tracks the **lineage DAG** (the graph of tasks that produced the object).

Ray automatically re-executes the upstream task graph to reconstruct the missing `ObjectRef` transparently!

Instructions:
1. Understand Ray's lineage recomputation mechanics.
2. Verify that lost object references are reconstructed on demand.
"""

import ray


# TODO: Define generate_numbers with max_retries=3
def generate_numbers(count: int) -> list[int]:
    return [i * 10 for i in range(count)]


# TODO: Define aggregate_sum remote task
def aggregate_sum(numbers: list[int]) -> int:
    return sum(numbers)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Build lineage DAG
    # numbers_ref = generate_numbers.remote(5)
    # sum_ref = aggregate_sum.remote(numbers_ref)
    # double_sum_ref = aggregate_sum.remote(numbers_ref)
    # sum_val, double_val = ray.get([sum_ref, double_sum_ref])
    sum_val, double_val = None, None

    assert sum_val == 100, f"Expected sum 100 (0+10+20+30+40), got {sum_val}"
    assert double_val == 100, f"Expected double sum 100, got {double_val}"
    print(f"✓ fault03 verified: Lineage DAG constructed and resolved successfully (sum={sum_val})!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
