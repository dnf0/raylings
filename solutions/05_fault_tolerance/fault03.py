"""Chapter 5: Fault Tolerance & Recovery - Solution 3: Lineage Reconstruction & DAG Replay.

Reference Solution for fault03.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray


@ray.remote(max_retries=3)
def generate_numbers(count: int) -> list[int]:
    return [i * 10 for i in range(count)]


@ray.remote
def aggregate_sum(numbers: list[int]) -> int:
    return sum(numbers)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    numbers_ref = generate_numbers.remote(5)
    sum_ref = aggregate_sum.remote(numbers_ref)
    double_sum_ref = aggregate_sum.remote(numbers_ref)
    sum_val, double_val = ray.get([sum_ref, double_sum_ref])

    assert sum_val == 100, f"Expected sum 100 (0+10+20+30+40), got {sum_val}"
    assert double_val == 100, f"Expected double sum 100, got {double_val}"
    print(f"✓ fault03 verified: Lineage DAG constructed and resolved successfully (sum={sum_val})!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
