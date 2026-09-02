"""Chapter 12: Ray Serve - Solution 2: Dynamic Request Batching (@serve.batch).

Reference Solution for serve02.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import serve


@serve.deployment
class BatchedPredictor:
    @serve.batch(max_batch_size=4, batch_wait_timeout_s=0.2)
    async def batch_predict(self, numbers: list[int]) -> list[int]:
        return [n * 2 for n in numbers]

    async def __call__(self, number: int) -> int:
        return await self.batch_predict(number)


def verify() -> None:
    ray.init(ignore_reinit_error=True)
    serve.start(http_options={"location": "NoServer"})

    handle = serve.run(BatchedPredictor.bind())
    assert handle is not None, "Handle must not be None"

    refs = [handle.remote(i) for i in [1, 2, 3, 4]]
    results = [r.result() for r in refs]
    assert results == [2, 4, 6, 8], f"Expected [2, 4, 6, 8], got {results}"
    print(f"✓ serve02 verified: Dynamic micro-batching coalesced requests successfully: {results}!")
    serve.shutdown()
    ray.shutdown()


if __name__ == "__main__":
    verify()
