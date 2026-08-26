"""Chapter 8: Ray Data for High-Throughput ETL - Solution 4: Filtering, Selection & Aggregation.

Reference Solution for data04.
"""

import ray
import ray.data


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [{"val": i, "category": "even" if i % 2 == 0 else "odd"} for i in range(100)]
    ds = ray.data.from_items(items)

    even_ds = ds.filter(lambda row: row["category"] == "even")
    projected_ds = even_ds.select_columns(["val"])
    total_val = projected_ds.sum(on="val")

    assert total_val == 2450, f"Expected sum 2450, got {total_val}"
    print(
        f"✓ data04 verified: Filtered and aggregated distributed dataset (total_sum={total_val})!"
    )


if __name__ == "__main__":
    verify()
