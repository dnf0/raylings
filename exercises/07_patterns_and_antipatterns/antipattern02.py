"""Chapter 7: Production Patterns & Anti-Patterns - Exercise 2: Fixing Fine-Grained Task Overhead.

Anti-Pattern: Micro-Tasks.
Every Ray remote task invocation carries a small scheduling, RPC, and serialization overhead
(typically ~100-300 microseconds). If your workload submits 10,000 tasks that each do 1 microsecond
of computation (e.g. `add.remote(1, 1)`), the execution time will be 99.9% scheduling overhead!

Correct Pattern: Batching / Chunking.
Group items into batches (e.g. chunks of 500 or 1,000 items) so that each task executes for at least
several milliseconds, achieving near-linear speedups across cores.

```python
# Bad: 1,000 tasks for 1,000 numbers
refs = [process_one.remote(x) for x in range(1000)]

# Good: Chunked tasks
def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

refs = [process_batch.remote(batch) for batch in chunk(range(1000), 200)]
```

Your Task:
- Define `@ray.remote` task `batch_square(numbers: list[int]) -> list[int]`:
  - Returns a new list containing `[x * x for x in numbers]`.
- In `verify()`:
  - Given `items = list(range(100))`.
  - Batch `items` into 4 equal chunks of 25 items each.
  - Dispatch `batch_square.remote(chunk)` across all 4 chunks.
  - Collect the results with `ray.get()`, flatten into a single list, and verify it matches `[x*x for x in range(100)]`.
"""

import ray


# TODO: Define batch_square remote task
def batch_square(numbers: list[int]) -> list[int]:
    return [x * x for x in numbers]


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = list(range(100))
    chunk_size = 25

    # TODO: Split items into chunks of 25 and dispatch batch_square
    # chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
    # refs = [batch_square.remote(chunk) for chunk in chunks]
    # batch_results = ray.get(refs)
    # flattened = [val for sublist in batch_results for val in sublist]
    flattened = []

    expected = [x * x for x in range(100)]
    assert flattened == expected, f"Expected 100 squared items, got {len(flattened)} items"
    print(
        f"✓ antipattern02 verified: Batched processing completed cleanly with 4 tasks ({len(flattened)} elements)!"
    )


if __name__ == "__main__":
    verify()
