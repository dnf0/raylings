"""
Exercise: exercises/12_ray_serve/serve02.py
Topic: Dynamic Dynamic Request Batching with @serve.batch

Context & Why:
Machine learning models (especially GPUs) achieve peak throughput when processing batches rather than
single requests.
`@serve.batch(max_batch_size=8, batch_wait_timeout_s=0.05)` dynamically buffers individual incoming HTTP
requests into a single vectorized batch before passing it to the inference function.

Instructions:
1. Decorate inference method with `@serve.batch`.
2. Send multiple concurrent requests and verify they are processed in batches.
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
