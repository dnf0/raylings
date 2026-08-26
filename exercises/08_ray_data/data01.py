# I AM NOT DONE
"""Chapter 8: Ray Data for High-Throughput ETL - Exercise 1: Datasets & Block Partitioning.

Ray Data provides distributed data processing for ML pipelines and ETL workloads.
Unlike Spark or Pandas, Ray Data is designed from the ground up for streaming execution,
heterogeneous CPU/GPU compute, and zero-copy integration with PyTorch/TensorFlow.

Key Concepts:
- `ray.data.from_items(items)`: Creates a dataset from a list of dicts.
- `ds.repartition(num_blocks=k)`: Redistributes data across `k` balanced blocks for parallelism.
- `ds.materialize()`: Executes lazy transformations into an in-memory `MaterializedDataset`.
- `ds.num_blocks()`: Returns the number of physical partitions/blocks in the materialized dataset.
- `ds.count()`: Computes total number of rows.

Your Task:
- In `verify()`:
  - Create a dataset of 100 items with `items = [{'val': i, 'squared': i * i} for i in range(100)]` using `ray.data.from_items(items)`.
  - Repartition into 4 blocks and materialize using `ds.repartition(num_blocks=4).materialize()`.
  - Assert that `ds.num_blocks() == 4`.
  - Assert that `ds.count() == 100`.
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
