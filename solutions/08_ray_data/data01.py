"""Chapter 8: Ray Data for High-Throughput ETL - Solution 1: Datasets & Block Partitioning.

Reference Solution for data01.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
import ray.data


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [{"val": i, "squared": i * i} for i in range(100)]
    ds = ray.data.from_items(items)
    ds = ds.repartition(num_blocks=4).materialize()

    num_blocks = ds.num_blocks()
    total_count = ds.count()

    assert num_blocks == 4, f"Expected 4 blocks, got {num_blocks}"
    assert total_count == 100, f"Expected count 100, got {total_count}"
    print(
        f"✓ data01 verified: Ray Dataset partitioned into {num_blocks} blocks with {total_count} rows!"
    )


if __name__ == "__main__":
    verify()
