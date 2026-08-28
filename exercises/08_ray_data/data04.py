"""
Exercise: exercises/08_ray_data/data04.py
Topic: Streaming Backpressure & Bounded Memory Windows

Context & Why:
When reading a 10TB dataset, loading all data into memory at once causes Out-Of-Memory (OOM) crashes.
Ray Data streams blocks through an execution pipeline using **dynamic backpressure**:
upstream operators only produce new blocks when downstream operators have capacity to consume them.

Instructions:
1. Configure bounded streaming windows and iterate through dataset batches without memory explosion.
"""

import ray
import ray.data


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [{"val": i, "category": "even" if i % 2 == 0 else "odd"} for i in range(100)]
    ds = ray.data.from_items(items)

    # TODO: Filter for even category, select 'val', and sum 'val'
    # even_ds = ds.filter(lambda row: row["category"] == "even")
    # projected_ds = even_ds.select_columns(["val"])
    # total_val = projected_ds.sum(on="val")
    total_val = None

    assert total_val == 2450, f"Expected sum 2450, got {total_val}"
    print(
        f"✓ data04 verified: Filtered and aggregated distributed dataset (total_sum={total_val})!"
    )


if __name__ == "__main__":
    verify()
