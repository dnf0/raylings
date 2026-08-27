"""Chapter 12: Ray Serve - Exercise 2: Dynamic Request Batching (@serve.batch).

High-throughput ML serving requires micro-batching concurrent individual HTTP requests
into unified batches to saturate GPU tensors and vectorized operations.

Key Concepts:
- `@serve.batch(max_batch_size=4, batch_wait_timeout_s=0.1)`: Decorates a method to coalesce calls.
- Individual client callers see normal 1-to-1 semantics, while Serve automatically batches under the hood.

Your Task:
- In `BatchedPredictor`:
  - Define `@serve.batch(max_batch_size=4, batch_wait_timeout_s=0.2)` on `batch_predict(self, numbers: list[int]) -> list[int]`.
  - In `batch_predict`, double each number: `[n * 2 for n in numbers]`.
  - In `__call__(self, number: int) -> int`, delegate to `await self.batch_predict(number)`.
- In `verify()`:
  - Dispatch 4 concurrent requests in parallel via `handle.remote(n)`.
  - Assert that all 4 returned the doubled values `[2, 4, 6, 8]`.
"""

# I AM NOT DONE
import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import serve


@serve.deployment
class BatchedPredictor:
    # TODO: Implement @serve.batch method and __call__
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Deploy BatchedPredictor and test concurrent batched queries
    handle = None

    assert handle is not None, "Handle must not be None"
    refs = [handle.remote(i) for i in [1, 2, 3, 4]]
    results = [r.result() for r in refs]
    assert results == [2, 4, 6, 8], f"Expected [2, 4, 6, 8], got {results}"
    print(f"✓ serve02 verified: Dynamic micro-batching coalesced requests successfully: {results}!")
    serve.shutdown()
    ray.shutdown()


if __name__ == "__main__":
    verify()
