"""
Exercise: exercises/08_ray_data/data01.py
Topic: Ray Data Ingestion & Block Partitioning

Context & Why:
Ray Data is a scalable, distributed data processing engine designed for ML datasets.
Datasets in Ray Data are partitioned into **Blocks** (backed by Apache Arrow tables).
Each block is stored in the Plasma object store and processed independently across workers.

Controlling block count (`override_num_blocks`) ensures balanced parallelism and prevents memory spills.

Instructions:
1. Create a Ray Dataset using `ray.data.from_items()` or `read_parquet()`.
2. Inspect block partitioning, schema, and dataset count.
"""

import ray
import ray.data


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [{"val": i, "squared": i * i} for i in range(100)]

    # TODO: Create Ray Dataset, repartition to 4 blocks, and materialize
    # ds = ray.data.from_items(items)
    # ds = ds.repartition(num_blocks=4).materialize()
    # num_blocks = ds.num_blocks()
    # total_count = ds.count()
    num_blocks, total_count = None, None

    assert num_blocks == 4, f"Expected 4 blocks, got {num_blocks}"
    assert total_count == 100, f"Expected count 100, got {total_count}"
    print(
        f"✓ data01 verified: Ray Dataset partitioned into {num_blocks} blocks with {total_count} rows!"
    )


if __name__ == "__main__":
    verify()
