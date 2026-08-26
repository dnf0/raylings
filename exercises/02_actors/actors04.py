# I AM NOT DONE
"""Chapter 2: Distributed State & Actors - Exercise 4: Async Actors & Concurrency.

By default, an actor executes one method call at a time. If a method does I/O
(e.g., waiting on an API, querying a database, or calling `asyncio.sleep`), standard
actors will block other incoming method calls until that I/O completes.

Ray supports Async Actors to achieve high-throughput concurrent I/O:
1. Define methods using `async def` and `await`.
2. Configure `@ray.remote(max_concurrency=N)` (where `N` is the maximum number of
   concurrent coroutines running on the actor's event loop).

Example:
    @ray.remote(max_concurrency=10)
    class AsyncFetcher:
        async def fetch(self, url):
            await asyncio.sleep(1.0)  # Non-blocking pause
            return f"data from {url}"

Key Differences:
- Standard Actor: Processes 1 call at a time sequentially.
- Async Actor: Processes up to `max_concurrency` calls concurrently on a single thread event loop.

Your Task:
- Decorate `AsyncRateLimiter` with `@ray.remote(max_concurrency=5)`.
- Implement `async def process_request(self, req_id: int, delay: float) -> str`.
- Issue 4 requests concurrently (each with a 0.08s delay).
- Verify that all requests complete and total elapsed time is under 0.20s (proving concurrent execution rather than 4 * 0.08s = 0.32s).
"""

import asyncio  # noqa: F401
import time  # noqa: F401
import ray


# TODO: Decorate with @ray.remote(max_concurrency=5)
class AsyncRateLimiter:
    def __init__(self) -> None:
        self.served_count = 0

    # TODO: Implement async def process_request(self, req_id: int, delay: float) -> str
    def process_request(self, req_id: int, delay: float) -> str:
        # await asyncio.sleep(delay)
        # self.served_count += 1
        # return f"req_{req_id}_ok"
        pass

    async def get_served_count(self) -> int:
        return self.served_count


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Instantiate AsyncRateLimiter
    # actor = AsyncRateLimiter.remote()
    # start = time.perf_counter()
    # refs = [actor.process_request.remote(i, 0.08) for i in range(4)]
    # results = ray.get(refs)
    # elapsed = time.perf_counter() - start
    # count = ray.get(actor.get_served_count.remote())
    results, elapsed, count = None, 999.0, 0

    expected_results = ["req_0_ok", "req_1_ok", "req_2_ok", "req_3_ok"]
    assert results == expected_results, f"Expected {expected_results}, got {results}"
    assert count == 4, f"Expected count 4, got {count}"
    print(f"Elapsed time for 4 concurrent async requests: {elapsed:.3f}s")
    assert elapsed < 0.22, f"Async actor took too long ({elapsed:.3f}s), concurrency not active"
    print("✓ actors04 verified: Async Actor max_concurrency coroutine concurrency confirmed!")


if __name__ == "__main__":
    verify()
