"""Chapter 8: Ray Data for High-Throughput ETL - Exercise 4: Filtering, Selection & Aggregation.

Ray Data provides relational operations to filter, select columns, and aggregate distributed datasets
in a single pipelined execution graph:

Key APIs:
- `ds.filter(fn)`: Filters rows satisfying a predicate function `row -> bool`.
- `ds.select_columns(cols)`: Drops unneeded columns for zero-copy projection.
- `ds.sum(on="col")` / `ds.mean(on="col")`: Computes distributed aggregations across blocks.

Example:
```python
filtered = ds.filter(lambda row: row["age"] >= 18)
projected = filtered.select_columns(["age", "score"])
avg_score = projected.mean(on="score")
```

Your Task:
- In `verify()`:
  - Create dataset from `[{'val': i, 'category': 'even' if i % 2 == 0 else 'odd'} for i in range(100)]`.
  - Filter for rows where `category == 'even'`.
  - Select only column `['val']`.
  - Compute the sum of `val` across the filtered dataset using `filtered.sum(on='val')`.
  - Assert that the sum is `2450` (sum of all even numbers from 0 to 98).
"""

# I AM NOT DONE
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
